import os
from flask import Flask, redirect, url_for


PLAID_ENV = os.getenv('PLAID_ENV', 'development')


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
        return redirect(url_for('auth.login'))

    from database import db
    db.init_app(app)

    import auth
    app.register_blueprint(auth.bp)

    import dashboard
    app.register_blueprint(dashboard.bp)

    import user
    app.register_blueprint(user.bp)

    return app
