from flmapp import db
from sqlalchemy import func, CheckConstraint
from sqlalchemy import and_, or_, desc

from datetime import datetime, timedelta


class PostMessage(db.Model):
    """投稿メッセージテーブル"""

    __tablename__ = 'PostMessage'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    PostMessage_id = db.Column(db.Integer, primary_key=True)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, Sell_id, from_user_id, message):
        self.Sell_id = Sell_id
        self.from_user_id = from_user_id
        self.message = message

    def create_new_postmessage(self):
        db.session.add(self)


class DealMessage(db.Model):
    """取引メッセージテーブル"""

    __tablename__ = 'DealMessage'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    DealMessage_id = db.Column(db.Integer, primary_key=True)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_checked = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, Sell_id, to_user_id, from_user_id, message):
        self.Sell_id = Sell_id
        self.to_user_id = to_user_id
        self.from_user_id = from_user_id
        self.message = message

    def create_new_dealmessage(self):
        db.session.add(self)

    @classmethod
    def get_messages_by_sell_id(cls, Sell_id, offset_value=0, limit_value=50):
        """Sell_id(item_id)によって取引メッセージレコードを得る"""
        return cls.query.filter_by(
            Sell_id = Sell_id
        ).order_by(desc(cls.DealMessage_id)).offset(offset_value).limit(limit_value).all()
        # 最新の50件が取り出される

    @classmethod
    def update_is_read_by_ids(cls, ids):
        """DealMessage_idが一致するレコードのis_readをTrueに更新する"""
        cls.query.filter(cls.DealMessage_id.in_(ids)).update(
            {'is_read':1},
            # レコードを更新する前にSELECTを実行して更新対象のレコードを取得する。
            # デフォルト値(設定しないと)IN句には対応していないためエラーになる。
            synchronize_session='fetch'
        )

    @classmethod
    def update_is_checked_by_ids(cls, ids):
        """DealMessage_idが一致するレコードのis_checkedをTrueに更新する"""
        cls.query.filter(cls.DealMessage_id.in_(ids)).update(
            {'is_checked':1},
            synchronize_session='fetch'
        )

    @classmethod
    def select_not_read_messages(cls, dest_user_id, self_user_id, sell_id):
        """相手から自分に対するメッセージでまだ読まれていないメッセージを取得"""
        return cls.query.filter(
            and_(
                cls.from_user_id == dest_user_id,
                cls.to_user_id == self_user_id,
                cls.Sell_id == sell_id,
                cls.is_read == 0
            )
        ).order_by(cls.DealMessage_id).all()

    @classmethod
    def select_not_checked_messages(cls, self_user_id, dest_user_id, sell_id):
        """自分から相手に対するメッセージで相手に読まれているが、自分がチェックしていないメッセージを取得"""
        return cls.query.filter(
            and_(
                cls.from_user_id == self_user_id,
                cls.to_user_id == dest_user_id,
                cls.Sell_id == sell_id,
                cls.is_read == 1,
                cls.is_checked == 0
            )
        ).order_by(cls.DealMessage_id).all()