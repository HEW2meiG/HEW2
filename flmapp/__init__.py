import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# LoginManagerの登録
login_manager = LoginManager()
# ログインページのviewを指定
login_manager.login_view = 'auth.login'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))

# sqlalchemyを通してflaskからdbアクセスをするための入り口
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # sessionを使う際にSECRET_KEYを設定
    app.config['SECRET_KEY'] =  b'R\x1c`\x8d\xed_\xe5\xd6\x8d\xef\xc6\x19g- J'

    # ここから /// データベースの設定
    # DBはSQLiteを使う
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    # ここまで /// データベースの設定
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 分割したblueprintを登録する
    from flmapp.views import auth
    from flmapp.views import mypage
    from flmapp.views import route

    app.register_blueprint(auth.bp)
    app.register_blueprint(mypage.bp)
    app.register_blueprint(route.bp)

    return app