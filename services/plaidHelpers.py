from database.db import get_db
from app import CLIENT
from plaid.errors import ItemError
from services.transactions import save_transactions


# CREATE account and transaction records for a newly created Item
def save_item_accounts(access_token):
    db = get_db()
    try:
        account_list = CLIENT.Accounts.get(access_token)
        for account in account_list['accounts']:
            db.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?)", (account['account_id'], account['mask'], account['name'], account['official_name'], account['type'], account['subtype'], access_token,))
            db.commit()
    except ItemError as e:
        print(e)

    save_transactions(access_token, start_date='2019-01-01')


# CREATE item mask
def create_mask(item_id):
    mask_slice = slice(len(item_id) - 4, len(item_id))
    item_mask = item_id[mask_slice]
    return item_mask
