from flmapp import db
from sqlalchemy import func, CheckConstraint
from flask_login import current_user

from datetime import datetime, timedelta
from uuid import uuid4


class UserTempToken(db.Model):
    """ユーザー仮登録トークン情報テーブル"""

    __tablename__ = 'UserTempToken'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    UserTempTokenToken_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        default=str(uuid4),
        nullable=False
    )
    email = db.Column(db.String(64), unique=True, nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, token, email, expire_at):
        self.token = token
        self.email = email
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, email):
        """ユーザー仮登録トークン情報テーブルにレコードの挿入をする"""
        token = str(uuid4())
        new_token = cls(
            token,
            email,
            # トークンの有効期限を1日に設定
            datetime.now() + timedelta(days=1) 
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, email):
        """トークンより仮登録したemailを返す"""
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.email
        else:
            return None

    @classmethod
    def get_user_id_by_email(cls, email):
        """emailより仮登録したレコードを抽出"""
        now = datetime.now()
        record = cls.query.filter_by(email=email).filter(cls.expire_at > now).first()
        if record:
            return record
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        """トークンの削除"""
        cls.query.filter_by(token=str(token)).delete()


class MailResetToken(db.Model):
    """メールリセットトークン情報テーブル"""

    __tablename__ = 'MailResetToken'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    MailResetToken_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        default=str(uuid4),
        nullable=False
    )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, token, User_id, email, expire_at):
        self.token = token
        self.User_id = User_id
        self.email = email
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, user, email):
        """メールリセットトークン情報テーブルにレコードの挿入をする"""
        token = str(uuid4())
        new_token = cls(
            token,
            user.User_id,
            email,
            # トークンの有効期限を1日に設定
            datetime.now() + timedelta(days=1) 
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        """トークンに紐づいたメールリセットトークン情報を返す"""
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record
        else:
            return None

    @classmethod
    def get_user_by_email(cls, email):
        """期限内のユーザーIDをemailで取り出す"""
        now = datetime.now()
        record = cls.query.filter_by(email=email).filter(cls.expire_at > now).first()
        if record:
            return record
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        """トークンの削除"""
        cls.query.filter_by(token=str(token)).delete()


class PasswordResetToken(db.Model):
    """パスワードリセットトークン情報テーブル"""

    __tablename__ = 'PasswordResetToken'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    PasswordResetToken_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        default=str(uuid4),
        nullable=False
    )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, token, User_id, expire_at):
        self.token = token
        self.User_id = User_id
        self.expire_at = expire_at

    @classmethod
    def publish_token(cls, user):
        """パスワードリセットトークン情報テーブルにレコードの挿入をする"""
        token = str(uuid4())
        new_token = cls(
            token,
            user.User_id,
            # トークンの有効期限を1日に設定
            datetime.now() + timedelta(days=1) 
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        """トークンに紐づいたユーザーIDを返す"""
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.User_id
        else:
            return None

    @classmethod
    def delete_token(cls, token):
        """トークンの削除"""
        cls.query.filter_by(token=str(token)).delete()
