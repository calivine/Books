import os
import csv
from flask import Blueprint, flash, url_for, render_template, request, session, jsonify, redirect, current_app as app
from werkzeug.utils import secure_filename
from database.db import get_db
from services.constants import UPLOAD_FOLDER
from services.utilities import format_date, allowed_file, db_assist, get_budget_period, convert_to_dict, set_date_window, format_transaction, update_name, get_monthly_spending, filter_pending


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# VIEW home dashboard
@bp.route('/home')
def home():
    user_id = session['user_id']         # User ID
    budget_period = get_budget_period()  # Current budget period
    print(budget_period)
    dates = set_date_window(7)           # Set window for transactions to be displayed

    # response = db_assist('select', 'activity')  # Select all transactions from activities table
    response = get_db().execute('SELECT * FROM activity Where date >= ? and date <= ?', (dates['start'], dates['end'], )).fetchall()

    categories_response = db_assist('select', 'budget', ['user_id', 'period'], [user_id, budget_period])

    for category in categories_response:
        print(category['category'])
    categories = db_assist('select', 'budget', ['user_id', 'period'], [user_id, budget_period])
    transactions = list(map(convert_to_dict, response))

    pending_transactions = filter_pending(transactions)

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


# CREATE new transaction data from input form
@bp.route('/save_transaction', methods=['POST'])
def save_transaction():
    # Retrieve data from form
    description = request.form['description']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['transaction_date']
    print(description)
    print(amount)
    print(category)
    print(date)
    # Package transaction in parameters list to be saved in database
    params = format_transaction(description, amount, date, category)
    # Save to activities table
    db_assist('insert', 'activity', params)
    print(params)
    return redirect(url_for('dashboard.home'))


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
                    amount = row[5] if row[6] == '' else '-'+row[6]
                    date = row[0].replace('/', '-')
                    date = format_date(date)
                    category = row[4]
                    description = row[3]
                    params = format_transaction(description, amount, date, category)
                    db_assist('insert', 'activity', params)
                    # get_db().execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                    # get_db().commit()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('dashboard.home'))



