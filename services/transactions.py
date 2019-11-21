import datetime
import plaid
from database.db import get_db
from app import client
from plaid.errors import APIError


def save_transactions(accounts, start_date='{:%Y-%m-%d}'.format(datetime.date.today() - datetime.timedelta(days=2)),
                      end_date='{:%Y-%m-%d}'.format(datetime.date.today())):
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
    for account in accounts:
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


