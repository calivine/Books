import os
import plaid
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify
from config.envSettings import CLIENT_ID, SECRET_KEY, PUBLIC_KEY
from database.db import get_db

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

bp = Blueprint('user', __name__, url_prefix='/user')


# VIEW item info
@bp.route('/accounts', methods=('GET', 'POST'))
def accounts():
    user_id = session['user_id']
    db = get_db()
    """
    account_list = db.execute('SELECT * FROM item i JOIN account a ON i.access_token = a.access_token WHERE user_id = ?', (user_id,)).fetchall()
    for act in account_list:
        print(act['id'])
    if len(account_list) == 0:
        account_list = db.execute(
            'SELECT * FROM item WHERE user_id = ?', (user_id,)).fetchall()
    """
    account_list = db.execute('SELECT * FROM item WHERE user_id = ?', (user_id,)).fetchall()

    return render_template('user/accounts.html', accounts=account_list,
                           plaid_environment=PLAID_ENV)


# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@bp.route('/get_access_token', methods=['POST'])
def get_access_token():
    client = plaid.Client(client_id=CLIENT_ID,
                          secret=SECRET_KEY,
                          public_key=PUBLIC_KEY,
                          environment=PLAID_ENV)
    db = get_db()
    public_token = request.form['public_token']
    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        print(e)

    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    print(access_token)
    print(item_id)
    mask_slice = slice(len(item_id)-4, len(item_id))
    item_mask = item_id[mask_slice]
    print(item_mask)
    db.execute("INSERT INTO item VALUES (?, ?, ?, ?)", (session['user_id'], access_token, item_id, item_mask,))
    db.commit()
    try:
        account_list = client.Accounts.get(access_token)
    except plaid.errors.PlaidError as e:
        print(e)
        return jsonify(exchange_response)
    for account in account_list['accounts']:
        db.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?)", (account['account_id'], account['mask'], account['name'], account['official_name'], account['type'],account['subtype'], access_token,))
        db.commit()
    return jsonify(exchange_response)


# CREATE/UPDATE accounts
@bp.route('/update/item/accounts/<item_id>')
def update_item_accounts(item_id):
    client = plaid.Client(client_id=CLIENT_ID,
                          secret=SECRET_KEY,
                          public_key=PUBLIC_KEY,
                          environment=PLAID_ENV)
    access_token = get_db().execute("SELECT access_token FROM item WHERE id = ?", (item_id,)).fetchone()
    try:
        response = client.Accounts.get(access_token['access_token'])
    except plaid.errors.PlaidError as e:
        print(e)
        return redirect(url_for('user.accounts'))
    for account in response['accounts']:
        print(account['account_id'], account['mask'], account['name'])
        test_account = get_db().execute("SELECT id FROM account WHERE id = ?", (account['account_id'],)).fetchone()
        print(test_account['id'])
        print(type(test_account['id']))
    # TODO: INSERT INTO account (id, mask, name, official_name, type, subtype, access_token) VALUES (?,?,?,?,?,?,?)
    return redirect(url_for('user.accounts'))

# UPDATE item
# Update credentials for Plaid Link
@bp.route('/update-account-link/<token>', methods=['GET'])
def update_account_link(token):
    client = plaid.Client(client_id=CLIENT_ID,
                          secret=SECRET_KEY,
                          public_key=PUBLIC_KEY,
                          environment=PLAID_ENV)

    # Get a new public token
    try:
        response = client.Item.public_token.create(token)
    except plaid.errors.PlaidError as e:
        print(e)

    public_token = response['public_token']

    return render_template('user/link_update.html',
                           public_token=public_token,
                           plaid_environment=PLAID_ENV)


# DELETE item
@bp.route('/delete/<access_token>', methods=['GET'])
def delete(access_token):
    client = plaid.Client(client_id=CLIENT_ID,
                          secret=SECRET_KEY,
                          public_key=PUBLIC_KEY,
                          environment=PLAID_ENV)
    try:
        response = client.Item.remove(access_token)
    except plaid.errors.PlaidError as e:
        print(e)
        return redirect(url_for('item.accounts'))
    if response['removed']:
        db = get_db()

        db.execute('DELETE FROM item WHERE access_token = ?', [access_token])
    return redirect(url_for('user.accounts'))

