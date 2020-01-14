from database.db import get_db
from datetime import datetime, timedelta
from services.constants import MONTH_STRING, ALLOWED_EXTENSIONS
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
    transaction_id = generate_random_alpha_num(37)
    params = (
        '',              # Account ID
        amount,          # Amount
        category,        # Category
        'category_id',   # Category ID
        date,            # Date
        'USD',           # ISO Currency Code
        description,     # Name
        0,               # Pending
        '',              # Pending Transaction ID
        transaction_id,  # Transaction ID
        'special',       # Transaction Type
        '',              # Category type
        '',              # Category name
        '',              # Sub-category
        ''               # Budget category
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
    get_db().execute('UPDATE activity SET name = ? WHERE transaction_id = ?', (description, trans_id,))
    get_db().commit()


# def update_category(category, trans_id)
# gets category name from id and updates the name based on category_name
def update_category_name(category, trans_id):
    get_db().execute('UPDATE activity SET budget_category = ? WHERE transaction_id = ?', (category, trans_id,))
    get_db().commit()


def pending(transaction):
    return transaction['pending']


def filter_pending(transactions):
    return filter(pending, transactions)


