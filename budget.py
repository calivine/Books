import os
import plaid
import datetime
from plaid.errors import APIError, ItemError
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify
from database.db import get_db

bp = Blueprint('budget', __name__, url_prefix='/budget')


@bp.route('/', methods=['GET'])
def budget():
    user_id = session['user_id']
    # Get current month and year and add as parameter for getting budget data
    budget = get_db().execute("SELECT * FROM budget WHERE user_id = ?", (user_id,)).fetchall()
    for item in budget:
        print(item['name'])

    return render_template('budget/index.html')

