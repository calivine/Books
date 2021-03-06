import os
import csv
import datetime
from Model import Model
from flask import Blueprint, flash, url_for, render_template, request, session, jsonify, redirect, current_app as app
from werkzeug.utils import secure_filename
from services.constants import UPLOAD_FOLDER, COLORS
from services.utilities import format_date, allowed_file, get_budget_period, set_date_window, format_transaction, update_name, update_category_name, filter_pending, format_amount, remaining, find


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# VIEW home dashboard
@bp.route('/home')
def home():
    update_time = datetime.time(4)
    now = datetime.datetime.now()

    print(update_time, now.time())
    user_id = session['user_id']         # User ID

    budget_period = get_budget_period()  # Current budget period

    dates = set_date_window(7)           # Set window for transactions to be displayed

    model = Model(user_id)               # Create database connection

    response = model.select('activity').where(('amount', '>=', 0), ('date', '>=', dates['start']), ('date', '<=', dates['end'])).get()

    for r in response:
        r['amount'] = format_amount(r['amount'])

    # Get category names from Budget table
    categories = model.select('budget', 'category').where(['user_id', '=', user_id], ['period', '=', budget_period]).get()
    budget = model.select('budget', 'category', 'planned', 'actual').where(['user_id', '=', user_id], ['period', '=', budget_period]).get()

    actual = find('actual', budget)
    planned = find('planned', budget)
    labels = find('categories', budget)

    remaining_budget = list(map(remaining, planned, actual))
    print(remaining_budget)
    transactions = response
    print(transactions)
    pending_transactions = filter_pending(transactions)

    for transaction in transactions:
        for pending in pending_transactions:
            # If processed transaction ID = pending ID
            if transaction['pending_transaction'] == pending['id']:
                print('found')
                pending_transactions.remove(pending)
        if transaction['id'] in pending_transactions:
            transactions.remove(transaction)

    print(pending_transactions)
    print(transactions)

    return render_template('dashboard/home.html', transactions=transactions, categories=categories, planned=planned, actual=actual, labels=labels, colors=COLORS[:len(planned)-1])


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


@bp.route('/update_category')
def update_category():
    category = request.args.get('update_name')
    trans_id = request.args.get('id')

    update_category_name(category, trans_id)

    return jsonify(description=category,
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
    # db_assist('insert', 'activity', params)
    model = Model(session['user_id'])
    model.insert('activity', params)
    print(params)

    return jsonify(params)


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
                    Model().insert('activity', params)
                    # db_assist('insert', 'activity', params)
                    # get_db().execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                    # get_db().commit()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return redirect(url_for('dashboard.home'))



