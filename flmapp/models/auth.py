from flmapp import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime, timedelta
from uuid import uuid4

#認証ユーザーの呼び出し方(idをuser_id)を定義
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#UserMixinを継承したUserクラス
class User(UserMixin, db.Model):

    __tablename__ = 'User'
    
    User_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(
        db.String(128),
        default=generate_password_hash('flmapp')
    )
    picture_path = db.Column(db.Text)
    prof_comment = db.Column(db.Text)
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, email):
        self.email = email

    def get_id(self):
        return (self.User_id)

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    @classmethod
    def select_user_by_id(cls, User_id):
        return cls.query.get(User_id)
    
    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True

class UserInfo(db.Model):

    __tablename__ = 'UserInfo'

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

class Address(db.Model):

    __tablename__ = 'Address'

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
 
class PasswordResetToken(db.Model):

    __tablename__ = 'PasswordResetToken'

    PasswordResetToken_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default=str(uuid4)
    )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, User_id, expire_at):
        self.token = token
        self.User_id = User_id
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, user):
        # パスワード設定用のURLを生成
        token = str(uuid4())
        new_token = cls(
            token,
            user.User_id,
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.User_id
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()
