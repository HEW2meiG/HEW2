from flmapp import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import func, CheckConstraint
from flask_login import UserMixin, current_user

from datetime import datetime, timedelta

@login_manager.user_loader
def load_user(user_id):
    """認証ユーザーの呼び出し方(idをuser_id)を定義"""
    return User.query.get(user_id)

#UserMixinを継承したUserクラス
class User(UserMixin, db.Model):
    """ユーザー情報テーブル"""

    __tablename__ = 'User'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)
    
    User_id = db.Column(db.Integer, primary_key=True)
    user_cord = db.Column(db.String(64), unique=True, index=True, nullable=False)
    username = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    picture_path = db.Column(db.Text, default='default.jpeg', nullable=False)
    prof_comment = db.Column(db.Text)
    default_ShippingAddress_id = db.Column(db.Integer, db.ForeignKey('ShippingAddress.ShippingAddress_id'))
    default_pay_way = db.Column(db.Integer, default=1, nullable=False)
    default_Credit_id = db.Column(db.Integer, db.ForeignKey('Credit.Credit_id'))
    is_active = db.Column(db.Boolean, default=True, nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, user_cord, username, email):
        self.user_cord = user_cord
        self.username = username
        self.email = email

    def create_new_user(self):
        db.session.add(self)

    def get_id(self):
        """load_userが受け取る引数"""
        return (self.User_id)

    # Custom property getter
    @property
    def password(self):
        raise AttributeError('パスワードは読み取り可能な属性ではありません。')

    # Custom property setter
    @password.setter
    def password(self, password):
        # generate_password_hash()：ハッシュ値が生成される
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """
        ユーザーのパスワードと引数のパスワードが正しいか判定する。
        一致していたらTrueを返す。
        """
        # check_password_hash():ハッシュ値が指定した文字列のものと一致しているか判定
        # 一致→True 不一致→False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def select_user_by_email(cls, email):
        """emailによってユーザーを得る"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def select_user_by_id(cls, User_id):
        """ユーザーIDによってユーザーを得る"""
        return cls.query.get(User_id)

    @classmethod
    def select_user_by_user_code(cls, user_code):
        """ユーザーコードによってユーザーを得る"""
        return cls.query.filter_by(user_code=user_code).first()


class UserInfo(db.Model):
    """ユーザー本人情報テーブル"""

    __tablename__ = 'UserInfo'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    UserInfo_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name_kana = db.Column(db.String(255), nullable=False)
    first_name_kana = db.Column(db.String(255), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, User_id, last_name, first_name, last_name_kana, first_name_kana, birth):
        self.User_id = User_id
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.birth = birth

    def create_new_userinfo(self):
        db.session.add(self)

    @classmethod
    def select_userinfo_by_user_id(cls):
        """ユーザーIDによってユーザー本人情報テーブルのレコードを取得する"""
        return cls.query.filter_by(User_id = current_user.get_id()).first()


class Address(db.Model):
    """住所情報テーブル"""

    __tablename__ = 'Address'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Address_id = db.Column(db.Integer, primary_key=True, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    prefecture = db.Column(db.String(64), nullable=False)
    address1 = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255), nullable=False)
    address3 = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, User_id, zip_code, prefecture, address1, address2, address3):
        self.User_id = User_id
        self.zip_code = zip_code
        self.prefecture = prefecture
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3

    def create_new_useraddress(self):
        db.session.add(self)

    @classmethod
    def select_address_by_user_id(cls):
        """ユーザーIDによって住所情報テーブルのレコードを取得する"""
        return cls.query.filter_by(User_id = current_user.get_id()).first()


class ShippingAddress(db.Model):
    """配送先住所情報テーブル"""

    __tablename__ = 'ShippingAddress'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    ShippingAddress_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name_kana = db.Column(db.String(255), nullable=False)
    first_name_kana = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    prefecture = db.Column(db.String(64), nullable=False)
    address1 = db.Column(db.String(255), nullable=False)
    address2 = db.Column(db.String(255), nullable=False)
    address3 = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
   
    def __init__(self, User_id, last_name, first_name, last_name_kana, first_name_kana, zip_code, prefecture, address1, address2, address3):
        self.User_id = User_id
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.zip_code = zip_code
        self.prefecture = prefecture
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3

    def create_new_shippingaddress(self):
        db.session.add(self)

    @classmethod
    def search_shippingaddress(cls, ShippingAddress_id):
        return cls.query.get(ShippingAddress_id)

    @classmethod
    def select_shippingaddresses_by_user_id(cls):
        return cls.query.filter_by(User_id = current_user.get_id()).all()

    @classmethod
    def delete_shippingaddress(cls, shippingaddress_id):
        """配送先住所レコードの削除"""
        cls.query.filter_by(ShippingAddress_id=shippingaddress_id).delete()


class Credit(db.Model):
    """クレジット情報テーブル"""

    __tablename__ = 'Credit'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)
    
    Credit_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    credit_name = db.Column(db.String(255), nullable=False) 
    credit_num = db.Column(db.Integer, nullable=False)
    expire = db.Column(db.Date, nullable=False)
    security_code_hash = db.Column(db.String(255), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, User_id, credit_name, credit_num, expire):
        self.User_id = User_id
        self.credit_name = credit_name
        self.credit_num = credit_num
        self.expire = expire

    def create_new_credit(self):
        db.session.add(self)

    # Custom property getter
    @property
    def security_code(self):
        raise AttributeError('セキュリティコードは読み取り可能な属性ではありません。')

    # Custom property setter
    @security_code.setter
    def security_code(self, security_code):
        # generate_password_hash()：ハッシュ値が生成される
        self.security_code_hash = generate_password_hash(security_code)

    @classmethod
    def search_credit(cls, Credit_id):
        return cls.query.get(Credit_id)

    @classmethod
    def select_credits_by_user_id(cls):
        return cls.query.filter_by(User_id = current_user.get_id()).all()
        
    @classmethod
    def delete_credit(cls, Credit_id):
        """支払い方法の削除"""
        cls.query.filter_by(Credit_id=Credit_id).delete()