from database.db import get_db
from datetime import datetime
from services.constants import month_strings


def format_date(date):
    split_date = date.split('-')
    month = split_date[0]
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

    prev_budget_period = '-'.join((month_strings[datetime.now().month - 2], str(datetime.now().year - 1)))
    print(prev_budget_period)
    new_sheet = db.execute("SELECT * FROM budget WHERE user_id = ? AND period = ?", (user_id, prev_budget_period,)).fetchall()
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
        db.execute("INSERT INTO budget (user_id, category, planned, actual, period) VALUES (?, ?, ?, ?, ?)", (budget_item['user_id'], budget_item['category'], budget_item['planned'], budget_item['actual'], budget_item['period'], ))
        db.commit()

    return monthly_budget
