from flmapp import db
from sqlalchemy import func, CheckConstraint

from datetime import datetime, timedelta

from enum import Enum
from flmapp.models.enum_conf import EnumType

# 出品情報テーブルのEnum型を定義
Genre = Enum("Genre", [("SF", 1), ("政治", 2), ("恋愛", 3), ("青春", 4), ("ミステリー", 5), \
            ("イヤミス", 6), ("歴史", 7), ("時代", 8), ("物語(短編)", 9), ("物語(中編)", 10), ("物語(長編)", 11)])
Item_state = Enum("Item_state", [("新品", 1), ("未使用に近い", 2), ("目立った傷や汚れなし", 3), \
                 ("やや傷や汚れあり", 4), ("傷や汚れあり", 5), ("全体的に状態が悪い", 6)])
Postage = Enum("Postage", [("送料込み(出品者負担)", 1), ("着払い(購入者負担)", 2)])
Send_way = Enum("Send_way", [("未定", 1), ("ゆうメール", 2), ("レターパック", 3), ("クロネコヤマト", 4), ("ゆうパック", 5), \
               ("クリックポスト", 6), ("ゆうパケット", 7)])
Schedule = Enum("Schedule", [("1日から2日で発送", 1), ("2日から3日で発送", 2), ("4日から7日で発送", 3)])
Deal_status = Enum("Deal_status", [("出品中", 1), ("取引中", 2), ("取引済み", 3)])

class Sell(db.Model):
    """出品情報テーブル"""

    __tablename__ = 'Sell'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Sell_id = db.Column(db.Integer, primary_key=True) 
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    sell_title = db.Column(db.String(255))  
    key1 = db.Column(db.String(255)) 
    key2 = db.Column(db.String(255))  
    key3 = db.Column(db.String(255)) 
    sell_comment = db.Column(db.Text)  
    price = db.Column(db.Integer)
    picture_path = db.Column(db.Text)
    genre = db.Column(EnumType(enum_class=Genre))
    item_state = db.Column(EnumType(enum_class=Item_state))
    postage = db.Column(EnumType(enum_class=Postage))  
    send_way = db.Column(EnumType(enum_class=Send_way))  
    consignor = db.Column(db.String(64))  
    schedule = db.Column(EnumType(enum_class=Schedule))
    remarks = db.Column(db.Text)
    deal_status = db.Column(EnumType(enum_class=Deal_status),default=Deal_status(1))
    sell_flg = db.Column(db.Boolean,default=True)
    is_active = db.Column(db.Boolean,default=True)
    has_sent = db.Column(db.Boolean,default=False)
    has_got = db.Column(db.Boolean,default=False)
    create_at = db.Column(db.DateTime,default=datetime.now)
    update_at = db.Column(db.DateTime,default=datetime.now)
    # Sellテーブルからデータを取得時にUserテーブルも取得
    sell_items = db.relationship('User', backref='sell', lazy='joined')

    def __init__(self, User_id, sell_title, key1, key2, key3, sell_comment, price, genre, item_state, \
                 postage, send_way, consignor, schedule, remarks):
        self.User_id = User_id
        self.sell_title = sell_title
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
        self.sell_comment = sell_comment
        self.price = price
        self.genre = Genre[genre]
        self.item_state = Item_state[item_state]
        self.postage = Postage[postage]
        self.send_way = Send_way[send_way]
        self.consignor = consignor
        self.schedule = Schedule[schedule]
        self.remarks = remarks

    def create_new_sell(self):
        db.session.add(self)