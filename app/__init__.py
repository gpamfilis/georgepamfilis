from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_featureflags import FeatureFlag
from config import config

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

csrf = CSRFProtect()
bootstrap = Bootstrap()
db = SQLAlchemy()
feature_flags = FeatureFlag()


def splits(string):
    return string.strip().split('/')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.jinja_env.filters['splits'] = splits
    csrf.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    feature_flags.init_app(app)
    login_manager.init_app(app)

    # TODO: organize the blueprints, rename
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
