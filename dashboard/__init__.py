from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import make_response
from flask import send_file
from flask_login import login_user, logout_user, login_required, LoginManager


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py', silent=True)


    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    with app.app_context():

        from . import models
        # Load all inbound routes
        from . import routes

        # Load all filters
        from . import filters

    return app
