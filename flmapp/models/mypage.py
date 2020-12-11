from flmapp import db

from datetime import datetime, timedelta
from flask_bcrypt import generate_password_hash

# 配送先住所テーブル
class ShippingAddress(db.Model):

    __tablename__ = 'ShippingAddress'

    ShippingAddress_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    last_name = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name_kana = db.Column(db.String(255))
    first_name_kana = db.Column(db.String(255))
    zip_code = db.Column(db.Integer)
    prefecture = db.Column(db.String(64))
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    address3 = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

# クレジット情報テーブル
class Credit(db.Model):

    __tablename__ = 'Credit'
    
    Credit_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    credit_name = db.Column(db.String(255)) 
    credit_num = db.column(db.Integer)
    expire = db.column(db.Date)
    security_code_hash = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)
    
    def __init__(self, User_id, credit_name, credit_num, expire):
        self.User_id = User_id
        self.credit_name = credit_name
        self.credit_num = credit_num
        self.expire = expire

    def create_new_credit(self):
        db.session.add(self)
        
    def save_security_code(self, security_code):
        self.security_code_hash = generate_password_hash(security_code)
        