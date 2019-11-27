from database.db import get_db
from datetime import datetime
from flask import Blueprint, render_template, session, request, jsonify
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


@bp.route('/update', methods=['POST'])
def update_budget():
    user_id = session['user_id']
    new_value = request.form['new_value']
    budget_period = request.form['budget_period']
    category = request.form['category']
    print(category)

    db = get_db()
    db.execute("UPDATE budget SET planned = ? WHERE user_id = ? AND period = ? AND category = ?", (new_value, user_id, budget_period, category, ))
    db.commit()

    return jsonify(new_value)

    




