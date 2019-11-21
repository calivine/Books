import datetime
import plaid
from database.db import get_db
from app import client
from plaid.errors import APIError, ItemError


# CREATE account and transaction records for a newly created Item
def initialize_new_item(access_token):
    db = get_db()
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


# CREATE item mask
def create_mask(item_id):
    mask_slice = slice(len(item_id) - 4, len(item_id))
    item_mask = item_id[mask_slice]
    return item_mask
