import os
import plaid
import datetime
from plaid.errors import APIError, ItemError
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify
from database.db import get_db
from app import client
from services.transactions import save_transactions
from services.plaidHelpers import initialize_new_item, create_mask

PLAID_ENV = os.getenv('PLAID_ENV', 'development')


bp = Blueprint('user', __name__, url_prefix='/user')


# VIEW account's Item overview
@bp.route('/items', methods=('GET', 'POST'))
def items():
    user_id = session['user_id']
    db = get_db()

    account_list = db.execute('SELECT * FROM item WHERE user_id = ?', (user_id,)).fetchall()

    save_transactions(account_list)

    return render_template('user/items.html', accounts=account_list,
                           plaid_environment=PLAID_ENV)


# EXCHANGE public token
# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@bp.route('/get_access_token', methods=['POST'])
def get_access_token():
    access_token = None
    exchange_response = None
    item_id = None

    db = get_db()
    public_token = request.form['public_token']

    try:
        exchange_response = client.Item.public_token.exchange(public_token)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
    except plaid.errors.PlaidError as e:
        print(e)

    item_mask = create_mask(item_id)
    print(item_mask)
    print(access_token)
    print(item_id)
    db.execute("INSERT INTO item VALUES (?, ?, ?, ?)", (session['user_id'], access_token, item_id, item_mask,))
    db.commit()
    initialize_new_item(access_token)

    return jsonify(exchange_response)


# UPDATE accounts
# Add account information associated with item
@bp.route('/item/account/details', methods=['POST'])
def get_account_details():
    item_details = None
    mask = request.form['item_mask']

    access_token = get_db().execute("SELECT access_token FROM item WHERE item_mask = ?", (mask,)).fetchone()
    try:
        item_response = client.Item.get(access_token['access_token'])
        item_details = {
            'item_id': item_response['item']['item_id'],
            'last_update': item_response['status']['transactions']['last_successful_update'],
            'last_failed_update': item_response['status']['transactions']['last_failed_update'],
            'institution': item_response['item']['institution_id']
        }
        print('Error: ', item_response['item']['error'])
    except ItemError as e:
        print(e)

    try:
        response = client.Accounts.get(access_token['access_token'])
        i = 1
        for account in response['accounts']:
            acct = 'account' + str(i)
            item_details[acct] = {
                'id': account['account_id'],
                'mask': account['mask'],
                'name': account['name'],
                'current_balance': account['balances']['current'],
                'available_balance': account['balances']['available']
            }
            i += 1
    except plaid.errors.PlaidError as e:
        print(e)

    # TODO: INSERT INTO account (id, mask, name, official_name, type, subtype, access_token) VALUES (?,?,?,?,?,?,?)
    return jsonify(item_details)


# UPDATE item
# Update credentials for Plaid Link
@bp.route('/update-account-link/<token>', methods=['GET'])
def update_account_link(token):

    public_token = None
    # Get a new public token
    try:
        response = client.Item.public_token.create(token)
        public_token = response['public_token']
    except plaid.errors.PlaidError as e:
        print(e)

    return render_template('user/link_update.html',
                           public_token=public_token,
                           plaid_environment=PLAID_ENV,
                           public_key=client.public_key)


# ROTATE access token
@bp.route('/rotate/access_token/<token>', methods=['GET'])
def rotate_access_token(token):
    db = get_db()
    access_token = db.execute("SELECT access_token, id FROM item WHERE item_mask = ?", (token,)).fetchone()
    try:
        response = client.Item.access_token.invalidate(access_token['access_token'])
        new_access_token = response['new_access_token']
        print(new_access_token)
        db.execute("UPDATE item SET access_token = ? WHERE id = ?", (new_access_token, access_token['id'],))
        db.commit()
    except plaid.errors.PlaidError as e:
        print(e)
    return redirect(url_for('user.items'))


# DELETE item
@bp.route('/delete/<access_token>', methods=['GET'])
def delete(access_token):
    db = get_db()
    try:
        response = client.Item.remove(access_token)
        print('Delete: ', response)
        print(type(response))
    except plaid.errors.PlaidError as e:
        print(e)

    db.execute('DELETE FROM item WHERE access_token = ?', (access_token,))
    db.commit()
    return redirect(url_for('user.items'))

