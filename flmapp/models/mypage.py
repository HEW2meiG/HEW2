from flmapp import db
from sqlalchemy import func, CheckConstraint

from datetime import datetime, timedelta

# 配送先住所テーブル
class ShippingAddress(db.Model):

    __tablename__ = 'ShippingAddress'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

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

    def create_new_usershippingaddress(self):
        db.session.add(self)
 

# クレジット情報テーブル
class Credit(db.Model):

    __tablename__ = 'Credit'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)
    
    Credit_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    credit_name = db.Column(db.String(255)) 
    credit_num = db.Column(db.Integer)
    expire = db.Column(db.Date)
    security_code = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)