import os
import plaid

from flask import Blueprint, render_template, request, session, jsonify
from config.envSettings import CLIENT_ID, SECRET_KEY, PUBLIC_KEY
from database.db import get_db

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def get_monthly_spending(transactions):
    total = 0
    for line in transactions:
        if line['budget'] == 'true' and line['category_id'] != '16000000':
            if line['amount'] > 0:
                total += line['amount']
    return total


# def update_name(description, trans_id)
# Function takes update_name and id
# gets transaction data based on id and updates the name based on update_name
def update_name(description, trans_id):
    get_db().execute('UPDATE activity SET name = ? WHERE transaction_id = ?', (description, trans_id,)).commit()


@bp.route('/home')
def home():
    user_id = session['user_id']
    client = plaid.Client(client_id=CLIENT_ID,
                          secret=SECRET_KEY,
                          public_key=PUBLIC_KEY,
                          environment=PLAID_ENV)

    accounts = get_db().execute('SELECT access_token FROM item WHERE user_id = ?', (user_id, )).fetchall()
    for account in accounts:
        response = client.Item.get(account['access_token'])
        print(response['status']['transactions']['last_successful_update'])
        print(response['status']['transactions']['last_failed_update'])
        print(response['item']['error'])


    return render_template('dashboard/home.html')


# Toggle transactions to be included in monthly budget
@bp.route('/toggle_budget')
def toggle_budget():
    global START_DATE
    global STOP_DATE
    db = get_db()
    transaction_id = request.args.get('transaction_id')

    transaction = db.execute('SELECT budget FROM activity Where transaction_id = ?', (transaction_id,)).fetchone()

    if transaction['budget'] == 'true':
        budget = 'false'
    else:
        budget = 'true'

    db.execute('UPDATE activity SET budget = ? WHERE transaction_id = ?', (budget, transaction_id,))

    print(START_DATE, STOP_DATE)
    transactions = db.execute('SELECT * FROM activity Where date >= ? and date <= ?', [START_DATE, STOP_DATE])

    spending = get_monthly_spending(transactions)
    return jsonify(spending=spending)


# Update transaction name
@bp.route('/update_description')
def update_description():
    description = request.args.get('update_name')
    trans_id = request.args.get('id')

    # Function takes update_name and id
    # gets transaction data based on id and updates the name based on update_name
    # def update_name(description, trans_id)
    update_name(description, trans_id)
    print(description)

    return jsonify(description=description,
                   id=trans_id)
