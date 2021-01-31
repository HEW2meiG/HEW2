from flmapp import db
from sqlalchemy import func, CheckConstraint
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, desc
from flask_login import UserMixin, current_user

from datetime import datetime, timedelta, date


class Likes(db.Model):
    """いいねログテーブル"""

    __tablename__ = 'Likes'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), primary_key=True, )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), primary_key=True)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, Sell_id, User_id):
        self.Sell_id = Sell_id
        self.User_id = User_id

    def create_new_likes(self):
        db.session.add(self)

    @classmethod
    def liked_exists(cls, Sell_id):
        """
        Sell_idとログイン中のユーザーIDが一致するいいねレコードを抽出し、
        レコードが存在すればTrue、
        存在しなければFalseを返す
        """
        record = cls.query.filter(
                    and_(
                        cls.Sell_id == Sell_id,
                        cls.User_id == current_user.get_id()
                    )
                ).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def select_likes_by_sell_id(cls, Sell_id):
        """Sell_idと一致する複数いいねレコードを抽出"""
        return cls.query.filter_by(Sell_id=Sell_id).all()

    @classmethod
    def delete_like(cls, Sell_id):
        """いいねレコードの削除"""
        return cls.query.filter(
            and_(
                cls.Sell_id == Sell_id,
                cls.User_id == current_user.get_id()
            )
        ).delete()

    @classmethod
    def likes_join_sell(cls, Sell, User_id):
        """
        LikesとSellを結合し,
        いいねしたUser_idと引数のUser_id
        が一致したSellレコードを新着順に取り出す
        """
        sell = aliased(Sell)
        return cls.query.filter(
            cls.User_id == User_id
        ).outerjoin(
            sell
        ).with_entities(
            sell
        ).order_by(desc(cls.create_at)).all()


class UserConnect(db.Model):
    """フォロー情報テーブル"""

    __tablename__ = 'UserConnect'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    UserConnect_id = db.Column(db.Integer, primary_key=True)
    to_user_id = db.Column(db.Integer,db.ForeignKey('User.User_id'), nullable=False)
    from_user_id = db.Column(db.Integer,db.ForeignKey('User.User_id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, to_user_id, from_user_id):
        self.to_user_id = to_user_id
        self.from_user_id = from_user_id

    def create_new_userconnect(self):
        db.session.add(self)

    @classmethod
    def followed_exists(cls, User_id):
        """
        引数のUser_idのユーザーをログイン中のユーザーが
        フォローしていればTrue、
        フォローしていなければFalseを返す
        """
        record = cls.query.filter(
                    and_(
                        cls.to_user_id == User_id,
                        cls.from_user_id == current_user.get_id()
                    )
                ).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def select_followers_by_user_id(cls, User_id):
        """to_user_idがUser_idと一致する複数レコードを抽出"""
        return cls.query.filter_by(to_user_id=User_id).all()

    @classmethod
    def select_follows_by_user_id(cls, User_id):
        """from_user_idがUser_idと一致する複数レコードを抽出"""
        return cls.query.filter_by(from_user_id=User_id).all()

    @classmethod
    def delete_follow(cls, User_id):
        """フォローレコードの削除"""
        return cls.query.filter(
                    and_(
                        cls.to_user_id == User_id,
                        cls.from_user_id == current_user.get_id()
                    )
                ).delete()

    @classmethod
    def select_timeline_sell(cls, Sell):
        """
        SellとUserConnectを結合し
        ログインしているユーザー以外かつ
        フォローしているユーザーが出品しているかつ
        出品状態、有効フラグが有効の商品を新着順に取り出す
        """
        sell = aliased(Sell)
        return cls.query.filter(
            cls.from_user_id == current_user.User_id
        ).outerjoin(
            sell,
            and_(
                sell.sell_flg == True, 
                sell.is_active == True,
                sell.User_id != current_user.User_id
            )
        ).with_entities(
            sell
        ).order_by(desc(cls.create_at)).all()


class BrowsingHistory(db.Model):
    """閲覧履歴テーブル"""

    __tablename__ = 'BrowsingHistory'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    BrowsingHistory_id = db.Column(db.Integer, primary_key=True)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    create_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime,default=datetime.now, nullable=False)

    def __init__(self, Sell_id, User_id):
        self.Sell_id = Sell_id
        self.User_id = User_id

    def create_new_browsinghistory(self):
        db.session.add(self)

    @classmethod
    def b_history_join_sell(cls, Sell, User_id):
        """
        BrowsingHistoryとSellを結合し,
        閲覧したUser_idと引数のUser_id
        が一致したSellレコードを新着順に3件取り出す
        """
        sell = aliased(Sell)
        return cls.query.filter(
            cls.User_id == User_id
        ).outerjoin(
            sell,
            and_(
                sell.User_id != User_id,
                sell.sell_flg == True, 
                sell.is_active == True
            )
        ).distinct(sell.Sell_id).with_entities(
            sell
        ).order_by(desc(cls.create_at)).limit(3).all()


    @classmethod
    def select_hit_sell(cls, Sell):
        """
        SellとBrowsingHistoryを結合し
        出品状態、有効フラグが有効の商品を
        今日の日付で閲覧数が多い順に取り出す
        """
        sell = aliased(Sell)
        now = datetime.now()
        return cls.query.filter(
            cls.create_at > now - timedelta(days=1)
        ).outerjoin(
            sell,
            and_(
                sell.Sell_id == cls.Sell_id,
                sell.sell_flg == True, 
                sell.is_active == True
            )
        ).with_entities(
            sell
        ).order_by(
            desc(func.count())
        ).group_by(
            cls.Sell_id
        ).all()