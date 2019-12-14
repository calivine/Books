import os
import csv
from datetime import datetime
from flask import Blueprint, flash, url_for, render_template, request, session, jsonify, redirect, current_app as app
from werkzeug.utils import secure_filename
from database.db import get_db
from services.constants import month_strings
from services.generateString import generate_random_alpha_num
from services.utilities import format_date


PLAID_ENV = os.getenv('PLAID_ENV', 'development')

UPLOAD_FOLDER = 'storage/temp'

ALLOWED_EXTENSIONS = {'csv'}

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# VIEW home dashboard
@bp.route('/home')
def home():
    user_id = session['user_id']
    db = get_db()
    response = db.execute("SELECT * FROM activity").fetchall()
    budget_period = '-'.join((month_strings[datetime.now().month - 1], str(datetime.now().year)))
    # Get current month and year and add as parameter for getting budget data
    categories = db.execute("SELECT category FROM budget WHERE user_id = ? AND period = ?", (user_id, budget_period,)).fetchall()

    transactions = []
    for transaction in response:
        # Convert from SQL row to dict
        transaction = dict(transaction)
        print(transaction)
        # Create function to convert date into words with abbreviated months
        split_date = str(transaction['date']).split('-')
        transaction['date'] = ' '.join([split_date[2], month_strings[int(split_date[1])-1]])
        transactions.append(transaction)

    pending_transactions = []
    for transaction in transactions:
        if transaction['pending'] == 1:
            pending_transactions.append(transaction['transaction_id'])
    for transaction in transactions:
        if transaction['transaction_id'] in pending_transactions:
            transactions.remove(transaction)

    return render_template('dashboard/home.html', transactions=transactions, categories=categories)


# EDIT transaction budget
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


# EDIT transaction name
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


# UPLOAD and CREATE new transaction data from csv
@bp.route('/import_csv', methods=['POST'])
def import_csv():
    if request.method == 'POST':
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('dashboard.home'))
        file = request.files['file']

        print(file.filename)
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('dashboard.home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                    # Starting with first row of data, save to Activities table
                    # Convert values as needed/generate transaction IDs.
                    # Generate a Transaction ID
                    transaction_id = generate_random_alpha_num(37)
                    amount = row[5] if row[6] == '' else '-'+row[6]
                    date = row[0].replace('/', '-')
                    date = format_date(date)
                    params = (
                        '',
                        amount,
                        row[4],
                        'category_id',
                        date,
                        'USD',
                        row[3],
                        0,
                        '',
                        transaction_id,
                        'special',
                        'true',
                        '',     # Category type
                        '',     # Category name
                        '')     # Sub-category
                    get_db().execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                    get_db().commit()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return redirect(url_for('dashboard.home'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




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

