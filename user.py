import os
import plaid
import datetime
from plaid.errors import APIError, ItemError
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify
from database.db import get_db
from app import client

PLAID_ENV = os.getenv('PLAID_ENV', 'development')


bp = Blueprint('user', __name__, url_prefix='/user')


# VIEW account's Item overview
@bp.route('/items', methods=('GET', 'POST'))
def items():
    user_id = session['user_id']
    db = get_db()
    start = '{:%Y-%m-%d}'.format(datetime.date.today() - datetime.timedelta(days=2))
    end = '{:%Y-%m-%d}'.format(datetime.date.today())
    account_list = db.execute('SELECT * FROM item WHERE user_id = ?', (user_id,)).fetchall()

    # Check if data has already been saved in DB
    check_response = db.execute('SELECT transaction_id FROM activity WHERE date >= ? AND date <= ?', (start, end,)).fetchall()
    existing = []
    for check in check_response:
        existing.append(check['transaction_id'])
    if len(check_response) is None:
        print("empty")
    for account in account_list:
        try:
            transaction_details = client.Transactions.get(account['access_token'], start_date=start, end_date=end)
            # print(response['accounts'])
            # print(response['item'])
            for data in transaction_details['transactions']:
                if data['transaction_id'] not in existing:
                    params = (data['account_id'],
                              data['amount'],
                              str(data['category']),
                              data['category_id'],
                              data['date'],
                              data['iso_currency_code'],
                              data['name'],
                              data['pending'],
                              data['pending_transaction_id'],
                              data['transaction_id'],
                              data['transaction_type'],
                              'true',
                              'na',  # data['category_type'],
                              'na',  # data['category_name'],
                              'na',)  # data['sub_category'])
                    db.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                    db.commit()
        except plaid.errors.PlaidError as e:
            print(e)

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

    print(access_token)
    print(item_id)
    mask_slice = slice(len(item_id)-4, len(item_id))
    item_mask = item_id[mask_slice]
    print(item_mask)
    db.execute("INSERT INTO item VALUES (?, ?, ?, ?)", (session['user_id'], access_token, item_id, item_mask,))
    db.commit()
    try:
        account_list = client.Accounts.get(access_token)
        for account in account_list['accounts']:
            db.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?)", (account['account_id'], account['mask'], account['name'], account['official_name'], account['type'], account['subtype'], access_token,))
            db.commit()
    except ItemError as e:
        print(e)

    try:
        response = client.Transactions.get(access_token, start_date='2019-01-01', end_date='{:%Y-%m-%d}'.format(datetime.date.today()))
        for data in response['transactions']:
            params = (data['account_id'],
                      data['amount'],
                      str(data['category']),
                      data['category_id'],
                      data['date'],
                      data['iso_currency_code'],
                      data['name'],
                      data['pending'],
                      data['pending_transaction_id'],
                      data['transaction_id'],
                      data['transaction_type'],
                      'true',
                      'na',  # data['category_type'],
                      'na',  # data['category_name'],
                      'na',)  # data['sub_category'])
            db.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
            db.commit()
    except ItemError as e:
        print(e)

    return jsonify(exchange_response)


# UPDATE accounts
# Add account information associated with item
@bp.route('/update/item/accounts', methods=['POST'])
def update_item_accounts():
    mask = request.form['item_mask']

    access_token = get_db().execute("SELECT access_token FROM item WHERE item_mask = ?", (mask,)).fetchone()
    try:
        item_response = client.Item.get(access_token['access_token'])
        print('Error: ', item_response['item']['error'])
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

