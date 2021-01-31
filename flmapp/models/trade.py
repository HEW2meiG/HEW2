from flmapp import db
from sqlalchemy import func, CheckConstraint
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, desc

from datetime import datetime, timedelta

from flask_login import (
    current_user
)

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
    sell_title = db.Column(db.String(255), nullable=False)  
    key1 = db.Column(db.String(255), nullable=False) 
    key2 = db.Column(db.String(255), nullable=False)  
    key3 = db.Column(db.String(255), nullable=False) 
    sell_comment = db.Column(db.Text, nullable=False)  
    price = db.Column(db.Integer, nullable=False)
    item_picture_path = db.Column(db.Text, default='default.png', nullable=False)
    genre = db.Column(EnumType(enum_class=Genre), nullable=False)
    item_state = db.Column(EnumType(enum_class=Item_state), nullable=False)
    postage = db.Column(EnumType(enum_class=Postage), nullable=False)  
    send_way = db.Column(EnumType(enum_class=Send_way), nullable=False)  
    consignor = db.Column(db.String(64), nullable=False)  
    schedule = db.Column(EnumType(enum_class=Schedule), nullable=False)
    remarks = db.Column(db.Text)
    deal_status = db.Column(EnumType(enum_class=Deal_status),default=Deal_status(1), nullable=False)
    sell_flg = db.Column(db.Boolean,default=True, nullable=False)
    is_active = db.Column(db.Boolean,default=True, nullable=False)
    has_sent = db.Column(db.Boolean,default=False, nullable=False)
    has_got = db.Column(db.Boolean,default=False, nullable=False)
    create_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    # Sellテーブルからデータを取得時にUserテーブルも取得
    user = db.relationship('User', backref='sell', lazy='joined', uselist=False)

    def __init__(self, User_id, sell_title, key1, key2, key3, sell_comment, price, item_picture_path, genre, item_state, \
                 postage, send_way, consignor, schedule, remarks):
        self.User_id = User_id
        self.sell_title = sell_title
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3
        self.sell_comment = sell_comment
        self.price = price
        self.item_picture_path = item_picture_path
        self.genre = Genre[genre]
        self.item_state = Item_state[item_state]
        self.postage = Postage[postage]
        self.send_way = Send_way[send_way]
        self.consignor = consignor
        self.schedule = Schedule[schedule]
        self.remarks = remarks

    def create_new_sell(self):
        db.session.add(self)

    @classmethod
    def select_sell_by_sell_id(cls, Sell_id):
        """Sell_id(item_id)によってSell(出品情報)レコードを得る"""
        return cls.query.get(Sell_id)

    @classmethod
    def select_sell_by_user_id(cls, User_id):
        """User_idによってSell(商品)レコードを得る"""
        return cls.query.filter(cls.User_id==User_id).all()

    @classmethod
    def select_sell_by_deal_status(cls, User_id, deal_status):
        """User_idとdeal_statusによってSell(商品)レコードを得る"""
        return cls.query.filter(cls.User_id==User_id, cls.deal_status==Deal_status(deal_status)).all()

    @classmethod
    def select_new_sell(cls):
        """
        出品状態、有効フラグが有効の商品を新着順に取り出す
        """
        return cls.query.filter_by(
            sell_flg = True, is_active = True
        ).order_by(desc(cls.create_at)).all()

    @classmethod
    def delete_sell(cls, Sell_id):
        """出品情報の削除"""
        cls.query.filter_by(Sell_id=Sell_id).delete()

    @classmethod
    def select_sales(cls, User_id):
        """売り上げ金を合計して返す"""
        return cls.query.filter(
            cls.User_id==current_user.User_id,
            cls.deal_status==Deal_status(3)
        ).with_entities(func.sum(Sell.price)).first()
    


class Buy(db.Model):
    """購入情報テーブル"""

    __tablename__ = 'Buy'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Buy_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    pay_way = db.Column(db.Integer, nullable=False)
    Credit_id = db.Column(db.Integer, db.ForeignKey('Credit.Credit_id'), nullable=False)
    ShippingAddress_id = db.Column(db.Integer, db.ForeignKey('ShippingAddress.ShippingAddress_id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, User_id, Sell_id, pay_way, Credit_id, ShippingAddress_id):
        self.User_id = User_id
        self.Sell_id = Sell_id
        self.pay_way = pay_way
        self.Credit_id = Credit_id
        self.ShippingAddress_id = ShippingAddress_id

    def create_new_buy(self):
        db.session.add(self)

    @classmethod
    def select_buy_by_sell_id(cls, Sell_id):
        """Sell_id(item_id)によってBuy(購入情報)レコードを得る"""
        return cls.query.filter_by(Sell_id=Sell_id).first()

    @classmethod
    def buy_join_sell_deal_status(cls, User_id, deal_status):
        """
        Buy(購入)とSell(商品)を結合し、
        BuyのUser_idとSellのdeal_statusが引数と一致するものを
        絞り込む
        """
        sell = aliased(Sell)
        return cls.query.filter(
            cls.User_id==User_id
        ).outerjoin(sell, sell.deal_status==Deal_status(deal_status)
        ).with_entities(sell).all()


# 相互評価情報テーブルのEnum型を定義
Rating_enum = Enum("rating", [("良い", 1), ("悪い", 2)])

class Rating(db.Model):
    """相互評価情報テーブル"""

    __tablename__ = 'Rating'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Rating_id = db.Column(db.Integer, primary_key=True)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    rating = db.Column(EnumType(enum_class=Rating_enum), nullable=False)
    rating_message = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, Sell_id, to_user_id, from_user_id, rating, rating_message):
        self.Sell_id = Sell_id
        self.to_user_id = to_user_id
        self.from_user_id = from_user_id
        self.rating = Rating_enum(rating)
        self.rating_message = rating_message

    def create_new_rating(self):
        db.session.add(self)

    @classmethod
    def select_rate_by_user_id(cls, User_id):
        """User_idのユーザーが評価されたレコードを抽出し、良いと悪いをカウントした値を返す"""
        good_ratings = cls.query.filter(
            and_(
                cls.to_user_id == User_id,
                cls.rating == Rating_enum(1)
            )
                ).all()
        bad_ratings = cls.query.filter(
            and_(
                cls.to_user_id == User_id,
                cls.rating == Rating_enum(2)
            )
                ).all()
        return len(good_ratings),len(bad_ratings)