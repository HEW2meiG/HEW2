from flmapp import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import func, CheckConstraint
from flask_login import UserMixin, current_user

from datetime import datetime, timedelta
from uuid import uuid4

#認証ユーザーの呼び出し方(idをuser_id)を定義
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#UserMixinを継承したUserクラス
# ユーザー情報テーブル
class User(UserMixin, db.Model):

    __tablename__ = 'User'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)
    
    User_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(
        db.String(128),
        default=generate_password_hash('flmapp')
    )
    picture_path = db.Column(db.Text)
    prof_comment = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)
    sell_items = db.relationship('Sell', backref='user', lazy='joined', uselist=False)

    def __init__(self, email):
        self.email = email

    def get_id(self):
        return (self.User_id)

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    # ユーザーのパスワードと引数のパスワードが正しいか
    def validate_password(self, password):
        # check_password_hash():ハッシュ値が指定した文字列のものと一致しているか判定
        # 一致→True 不一致→False
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    # ユーザーIDによってユーザーを得る
    @classmethod
    def select_user_by_id(cls, User_id):
        return cls.query.get(User_id)
    
    # パスワード更新処理
    def save_new_password(self, new_password):
        # generate_password_hash()：ハッシュ値が生成される
        self.password = generate_password_hash(new_password)
        # 有効フラグをTrue
        self.is_active = True

# ユーザー本人情報テーブル
class UserInfo(db.Model):

    __tablename__ = 'UserInfo'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    UserInfo_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    last_name = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name_kana = db.Column(db.String(255))
    first_name_kana = db.Column(db.String(255))
    birth = db.Column(db.Date)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, User_id, last_name, first_name, last_name_kana, first_name_kana, birth):
        self.User_id = User_id
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.birth = birth

    def create_new_userinfo(self):
        db.session.add(self)

    # ユーザーIDによってユーザーを得る
    @classmethod
    def select_user_by_id(cls):
        return cls.query.filter_by(User_id = current_user.get_id()).first()


# 住所情報テーブル
class Address(db.Model):

    __tablename__ = 'Address'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Address_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    zip_code = db.Column(db.Integer)
    prefecture = db.Column(db.String(64))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    address3 = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, User_id, zip_code, prefecture, address1, address2, address3):
        self.User_id = User_id
        self.zip_code = zip_code
        self.prefecture = prefecture
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3

    def create_new_useraddress(self):
        db.session.add(self)

    #ユーザーIDによって住所情報テーブルのレコードを取得する。
    @classmethod
    def select_user_by_id(cls):
        #住所情報テーブルの最初のレコードをクラスで返す
        return cls.query.filter_by(User_id = current_user.get_id()).first()
 
# パスワードリセットトークン情報テーブル
class PasswordResetToken(db.Model):

    __tablename__ = 'PasswordResetToken'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    PasswordResetToken_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default=str(uuid4)
    )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    # 期限
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, User_id, expire_at):
        self.token = token
        self.User_id = User_id
        self.expire_at = expire_at

    #パスワードリセットトークン情報テーブルにレコードの挿入
    @classmethod
    def publish_token(cls, user):
        # パスワード設定用のURLを生成
        token = str(uuid4())
        new_token = cls(
            token,
            user.User_id,
            # トークンの有効期限を1日に設定
            datetime.now() + timedelta(days=1) 
        )
        db.session.add(new_token)
        return token
    
    # トークンに紐づいたユーザーIDを得る
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.User_id
        else:
            return None

    # トークン削除 
    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()
