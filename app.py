import os
import plaid
from flask import Flask, render_template
from config.envSettings import CLIENT_ID, SECRET_KEY, PUBLIC_KEY

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

client = plaid.Client(client_id=CLIENT_ID,
                      secret=SECRET_KEY,
                      public_key=PUBLIC_KEY,
                      environment=PLAID_ENV,
                      api_version='2019-05-29')


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'books.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    from database import db
    db.init_app(app)

    import auth
    app.register_blueprint(auth.bp)

    import dashboard
    app.register_blueprint(dashboard.bp)

    import user
    app.register_blueprint(user.bp)

    import budget
    app.register_blueprint(budget.bp)

    return app
