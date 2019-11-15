import sqlite3

import click

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('database/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def seed_db():
    from database.seeder import seed_db
    seed_db()
    """
    db.execute('INSERT INTO user (name, password) VALUES (?,?)', ('alexc', generate_password_hash('alex')))
    db.commit()
    account_id = 'MgRoBAEb53UmLVrVezxdcZYLkMxPdXtMzD3qY'
    mask = '3165'
    name = 'TD SIMPLE SAVINGS'
    official_name = 'TD SIMPLE SAVINGS'
    account_type = 'depository'
    subtype = 'savings'
    access_token = 'access-development-a76d833e-70ce-45c8-bbb3-9ea2bc6d5bb7'
    item_id = 'OEX9y0o4bKIjgKBK98Y6uMjvDw8kzzC8mybay'

    db.execute('INSERT INTO item VALUES (?, ?, ?)', (1, access_token, item_id,))
    db.commit()

    db.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?)", (account_id, mask, name, official_name, account_type, subtype, access_token,))
    db.commit()"""


@click.command('init-db')
@with_appcontext
def init_db_command():
    """ Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    seed_db()
    click.echo('Seeded tables.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
