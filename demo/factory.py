from flask import Flask, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException
from flask.ext.admin import Admin

from config import config, Config

from .models import User, Group
from .core import db

def create_app(config_name='development'):
    """Flask factory function"""

    # Configure from config.py
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # Configure Flask-Admin
    admin = Admin(name='demo', template_mode='bootstrap3')
    from .admin_views import DbView
    admin.add_view(DbView(Group, db.session))
    admin.add_view(DbView(User, db.session))
    admin.init_app(app)

    # Blueprints
    from .api import groups_bp
    app.register_blueprint(groups_bp, url_prefix='/api/groups')

    from .api import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    #

    @app.before_first_request
    def create_tables():
        db.create_all()

    # Ensure all errors thrown are json
    # http://flask.pocoo.org/snippets/83/
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error

    return app
