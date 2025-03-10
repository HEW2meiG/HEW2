import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha
from flask_wtf.csrf import CSRFProtect

from flmapp.utils.template_filters import replace_newline

# LoginManagerの登録
login_manager = LoginManager()
# ログインページのviewを指定
login_manager.login_view = 'auth.login'
login_manager.login_message = 'ログインしてください'

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # sessionを使う際にSECRET_KEYを設定
    app.config['SECRET_KEY'] =  b'R\x1c`\x8d\xed_\xe5\xd6\x8d\xef\xc6\x19g- J'

    # ここから /// 画像アップロードの設定
    # 画像のアップロード先のディレクトリ
    app.config["IMAGE_UPLOADS"] = 'flmapp/static/user_image'
    app.config["ORIGINAL_IMAGE_UPLOADS"] = 'flmapp/static/original_user_image'
    app.config["ITEM_IMAGE_UPLOADS"] = 'flmapp/static/item_image'
    app.config["ITEM_TEMP_IMAGE_UPLOADS"] = 'flmapp/static/item_temp_image'
    app.config["ORIGINAL_ITEM_IMAGE_UPLOADS"] = 'flmapp/static/original_item_image'
    # アップロードされる拡張子の制限
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
    # 画像サイズの制限
    app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024
    # ここまで /// 画像アップロードの設定

    # ここから /// データベースの設定
    # DBはSQLiteを使う
    #! パスを変えてください
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + "/Users/shimomuramei/Desktop/set_prefs/data.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    # ここまで /// データベースの設定

    # ここから /// メール送信の設定
    app.config['DEBUG'] = True # デバッグのサポート
    app.config['TESTING'] = False
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'koshokaikou.official@gmail.com'
    app.config['MAIL_PASSWORD'] = 'qhfumxmrlcfxhmsr'
    app.config['MAIL_DEFAULT_SENDER'] = 'koshokaikou.official@gmail.com'
    app.config['MAIL_MAX_EMAILS'] = 5 #送信するメールの最大数
    app.config['MAIL_SUPPRESS_SEND'] = False
    app.config['MAIL_ASCII_ATTACHHMENTS'] = False
    # ここまで /// メール送信の設定

    # ここから /// キャプチャの設定
    app.config['CAPTCHA_ENABLE'] = True
    app.config['CAPTCHA_LENGTH'] = 5
    app.config['CAPTCHA_WIDTH'] = 160
    app.config['CAPTCHA_HEIGHT'] = 100
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    # ここまで /// キャプチャの設定
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    Session(app)
    captcha = FlaskSessionCaptcha(app)
    CSRFProtect(app)

    # カスタムテンプレートフィルターの登録
    app.add_template_filter(replace_newline)

    # 分割したblueprintを登録する
    from flmapp.views import (
        auth, mypage, route, sell, item, buy, transaction,
        ajax, user, history, search, todolist
    )

    app.register_blueprint(auth.bp)
    app.register_blueprint(mypage.bp)
    app.register_blueprint(route.bp)
    app.register_blueprint(sell.bp)
    app.register_blueprint(item.bp)
    app.register_blueprint(buy.bp)
    app.register_blueprint(transaction.bp)
    app.register_blueprint(ajax.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(todolist.bp)

    return app