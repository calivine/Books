from database.db import get_db
from datetime import datetime, timedelta
from services.constants import MONTH_STRING, ALLOWED_EXTENSIONS
from services.transactions import save_transactions
from Model import Model
import string
import random


def generate_random_string(base_string_character, string_size=10):
    response_string = ''
    for i in range(string_size):
        character = random.choice(base_string_character)

        # Append the selected character to the response string
        response_string += character
    return response_string


def generate_random_alpha_num(str_len=10):
    ret = generate_random_string(string.digits + string.ascii_letters, str_len)
    return ret


def set_date_window(days):
    start_date = '{:%Y-%m-%d}'.format(datetime.today() - timedelta(days=days))
    end_date = '{:%Y-%m-%d}'.format(datetime.today())
    dates = {'start': start_date,
             'end': end_date}
    return dates


# Returns the current budget period in string form
def get_budget_period():
    return '-'.join((MONTH_STRING[datetime.now().month - 1], str(datetime.now().year)))


# Returns a date string formatted for UI display
def get_date_string(date):
    split_date = str(date).split('-')
    return ' '.join([split_date[2], MONTH_STRING[int(split_date[1]) - 1]])


# Convert day from mm-dd-yyyy to yyyy-mm-dd
def format_date(date):
    split_date = date.split('-')

    month = '0' + split_date[0] if len(split_date[0]) == 1 else split_date[0]

    day = split_date[1]
    day = '0' + day if len(day) == 1 else day
    year = split_date[2]
    response_date = '-'.join([year, month, day])
    return response_date


# Create and save a new monthly budget tracking sheet
# Returns the new budget sheet
def new_budget_sheet(user_id, budget_period):
    db = get_db()
    print(budget_period)

    prev_budget_period = '-'.join((MONTH_STRING[datetime.now().month - 2], str(datetime.now().year - 1)))
    print(prev_budget_period)
    new_sheet = db.execute("SELECT * FROM budget WHERE user_id = ? AND period = ?",
                           (user_id, prev_budget_period,)).fetchall()
    print(new_sheet[0])
    monthly_budget = []
    for item in new_sheet:
        budget_item = {
            'user_id': user_id,
            'category': item['category'],
            'planned': item['planned'],
            'actual': 0,
            'period': budget_period
        }
        monthly_budget.append(budget_item)
        print(budget_item)
        db.execute("INSERT INTO budget (user_id, category, planned, actual, period) VALUES (?, ?, ?, ?, ?)", (
            budget_item['user_id'], budget_item['category'], budget_item['planned'], budget_item['actual'],
            budget_item['period'],))
        db.commit()

    return monthly_budget


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_plaid_category(category):
    return category


def format_capital_one_category(category):
    return category


def get_budget_category(category, data_format):
    return data_format(category)


def convert_to_dict(row):
    transaction = dict(row)
    transaction['date'] = get_date_string(transaction['date'])
    return transaction


def select(table, query):
    if query is None:
        return "SELECT * FROM " + table
    else:
        argument_list = []
        for arg in query:
            argument_list.append(str(arg) + " = ?")
        argument_list = " AND ".join(argument_list)
        return "SELECT * FROM " + table + " WHERE " + argument_list


def insert(table, query, args):
    if args is None:
        v = "?" * len(query)
        values = ",".join(v)
        x = "INSERT INTO " + table + " VALUES (" + values + ")"
    else:
        query_list = ",".join(query)
        # Repeat ? for each item in query
        v = "?" * len(args)
        values = ",".join(v)
        x = "INSERT INTO " + table + "(" + query_list + ") VALUES (" + values + ")"
    print(x)
    return x


def db_assist(command, table, query=None, args=None, opts=None):
    response = None
    if command == 'select':
        s = select(table, query)
        print(s)
        if query is not None:
            response = get_db().execute(s, args, ).fetchall()
        else:
            response = get_db().execute(s)
    elif command == 'insert':
        x = insert(table, query, args)
        get_db().execute(x, query)
        get_db().commit()
        return
    return response


def format_transaction(description, amount, date, category):
    tid = generate_random_alpha_num(37)
    params = (
        '',              # Account ID
        amount,          # Amount
        category,        # Category
        '',              # Category ID
        date,            # Date
        'USD',           # ISO Currency Code
        description,     # Name
        0,               # Pending
        '',              # Pending Transaction ID
        tid,             # Transaction ID
        'special',       # Transaction Type
        '',              # Category type
        '',              # Category name
        '',              # Sub-category
        category         # Budget category
    )
    return params


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
    get_db().execute('UPDATE activity SET name = ? WHERE id = ?', (description, trans_id,))
    get_db().commit()


# def update_category(category, trans_id)
# gets category name from id and updates the name based on category_name
def update_category_name(category, trans_id):
    get_db().execute('UPDATE activity SET budget_category = ? WHERE id = ?', (category, trans_id,))
    get_db().commit()


# Returns the key, pending from a transactions dict
def pending(transaction):
    return transaction['pending']


def filter_pending(transactions):
    return list(filter(pending, transactions))


# Add .00 or 0 to amounts for display
def format_amount(amount):
    amount = str(amount)
    if '.' in amount:
        if amount[len(amount) - 2] is '.':
            return amount + '0'
        else:
            return amount
    else:
        return amount + '.00'


# Function run by scheduler to update user accounts every 24 hours
def update_account(app):
    with app.app_context():
        accounts = Model().select('item').get()
    for account in accounts:
        with app.app_context():
            save_transactions(account['access_token'])
    print("Update Finished.")


def find(key, data):
    funcs = {
        'planned': return_planned,
        'actual': return_actual,
        'categories': return_categories
    }
    return filter_dict(funcs[key], data)


def filter_dict(func, data):
    return list(map(func, data))


def return_planned(d):
    return int(d['planned'])


def return_actual(d):
    return int(d['actual'])


def return_categories(d):
    return d['category']


# remaining()
def remaining(planned, actual):
    return int(planned) - int(actual)


# Update Actual budget amounts based on transaction data
def update_actuals(transactions, budget):
    for transaction in transactions:
        for category in budget:
            if transaction['category'] == category['category']:
                actual = int(budget['actual'])
                actual += int(transaction['amount'])
                budget['actual'] = actual
    return budget
