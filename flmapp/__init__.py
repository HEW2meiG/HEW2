import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] =  b'R\x1c`\x8d\xed_\xe5\xd6\x8d\xef\xc6\x19g- J'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from flmapp.views.auth import bp
    app.register_blueprint(bp)

    return app