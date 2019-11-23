from database.db import get_db
from datetime import datetime
from flask import Blueprint, render_template, session, request
from config.envSettings import month_strings

bp = Blueprint('budget', __name__, url_prefix='/budget')


@bp.route('/', methods=['GET'])
def budget():
    user_id = session['user_id']
    print(datetime.now().month, datetime.now().year)
    print(month_strings[datetime.now().month - 1])
    budget_period = '-'.join((month_strings[datetime.now().month - 1], str(datetime.now().year)))
    print(budget_period)
    # Get current month and year and add as parameter for getting budget data
    monthly_budget = get_db().execute("SELECT * FROM budget WHERE user_id = ? AND period = ?", (user_id, budget_period,)).fetchall()
    for item in monthly_budget:
        print(item['category'])

    return render_template('budget/index.html', budget_sheet=monthly_budget)


@bp.route('/update')
def update_budget():
    current_value = request.args.get('current_value')



