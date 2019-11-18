import os
import plaid
from plaid.errors import APIError, ItemError
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify
from database.db import get_db
from app import client

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

bp = Blueprint('user', __name__, url_prefix='/user')


# VIEW item info
@bp.route('/items', methods=('GET', 'POST'))
def items():
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

    return render_template('user/items.html', accounts=account_list,
                           plaid_environment=PLAID_ENV)


# EXCHANGE public token
# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@bp.route('/get_access_token', methods=['POST'])
def get_access_token():
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
    except ItemError as e:
        print(e)
        return jsonify(exchange_response)
    for account in account_list['accounts']:
        db.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?)", (account['account_id'], account['mask'], account['name'], account['official_name'], account['type'],account['subtype'], access_token,))
        db.commit()
    return jsonify(exchange_response)


# UPDATE accounts
# Add account information associated with item
@bp.route('/update/item/accounts', methods=['POST'])
def update_item_accounts():
    mask = request.form['item_mask']

    access_token = get_db().execute("SELECT access_token FROM item WHERE item_mask = ?", (mask,)).fetchone()
    try:
        item_response = client.Item.get(access_token['access_token'])
        print('Products: ', item_response['item']['available_products'], item_response['item']['billed_products'])
        print('Last Successful Update: ', item_response['status']['transactions']['last_successful_update'])
        print('Last Failed Update: ', item_response['status']['transactions']['last_failed_update'])
        print('Institution ID: ', item_response['item']['institution_id'])
        print('Item ID: ', item_response['item']['item_id'])
        print('Error: ', item_response['item']['error'])
        last_update_time = item_response['status']['transactions']['last_successful_update']
    except ItemError as e:
        print(e)

    if item_response is not None:
        item_details = {
            'item_id': item_response['item']['item_id'],
            'last_update': item_response['status']['transactions']['last_successful_update'],
            'last_failed_update': item_response['status']['transactions']['last_failed_update'],
            'institution': item_response['item']['institution_id']
        }

    try:
        response = client.Accounts.get(access_token['access_token'])
    except plaid.errors.PlaidError as e:
        print(e)


    if response is not None:
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
            print(account['account_id'], account['mask'], account['name'], account['balances']['current'], account['balances']['available'])
    # TODO: INSERT INTO account (id, mask, name, official_name, type, subtype, access_token) VALUES (?,?,?,?,?,?,?)
    return jsonify(item_details)


# UPDATE item
# Update credentials for Plaid Link
@bp.route('/update-account-link/<token>', methods=['GET'])
def update_account_link(token):

    # Get a new public token
    try:
        response = client.Item.public_token.create(token)
    except plaid.errors.PlaidError as e:
        print(e)

    public_token = response['public_token']

    return render_template('user/link_update.html',
                           public_token=public_token,
                           plaid_environment=PLAID_ENV,
                           public_key=client.public_key)


# DELETE item
@bp.route('/delete/<access_token>', methods=['GET'])
def delete(access_token):
    try:
        response = client.Item.remove(access_token)
    except plaid.errors.PlaidError as e:
        print(e)
        return redirect(url_for('user.items'))
    if response['removed']:
        db = get_db()

        db.execute('DELETE FROM item WHERE access_token = ?', [access_token])
    return redirect(url_for('user.items'))

