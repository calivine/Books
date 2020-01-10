import datetime
import plaid
from database.db import get_db
from app import client
from plaid.errors import APIError


def save_transactions(access_token, start_date='{:%Y-%m-%d}'.format(datetime.date.today() - datetime.timedelta(days=7)), end_date='{:%Y-%m-%d}'.format(datetime.date.today())):
    db = get_db()
    start = start_date
    end = end_date

    # Check if data has already been saved in DB
    check_response = db.execute('SELECT transaction_id FROM activity WHERE date >= ? AND date <= ?',
                                (start, end,)).fetchall()
    existing = []
    for check in check_response:
        existing.append(check['transaction_id'])
    if len(check_response) is None:
        print("empty")
    try:
        transaction_details = client.Transactions.get(access_token, start_date=start, end_date=end)
        # print(response['accounts'])
        # print(response['item'])
        transactions = format_category(transaction_details['transactions'])
        for data in transactions:
            print(data['transaction_id'])
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
                          data['category_type'],
                          data['category_name'],
                          data['sub_category'],
                          '')
                db.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                db.commit()
    except plaid.errors.PlaidError as e:
        print(e)


# Separate out category terms
def format_category(accounts):
    # Cycle through each transaction in category
    # Break out each term into one of three columns
    for line in accounts:
        if line['category'] is not None:
            if len(line['category']) == 3:
                line['category_type'] = line['category'][0]
                line['category_name'] = line['category'][1]
                line['sub_category'] = line['category'][2]
            elif len(line['category']) == 2:
                line['category_type'] = line['category'][0]
                line['category_name'] = line['category'][1]
                line['sub_category'] = ""
            else:
                line['category_type'] = line['category'][0]
                line['category_name'] = ""
                line['sub_category'] = ""
        else:
            line['category_type'] = ""
            line['category_name'] = ""
            line['sub_category'] = ""
    return accounts
