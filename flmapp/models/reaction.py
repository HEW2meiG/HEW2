class Likes(db.Model):
    """いいねログテーブル"""

    __tablename__ = 'Likes'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    Sell_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('Sell.Sell_id'), nullable=False)
    User_id = db.Column(db.Integer, primary_key=True, db.ForeignKey('User.User_id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)


class UserConnect(db.Model):
    """フォロー情報テーブル"""

    __tablename__ = 'UserConnect'
    __table_args__ = (CheckConstraint('update_at >= create_at'),)

    UserConnect_id = db.Column(db.Integer, primary_key=True)
    to_user_id = db.Column(db.Integer,db.ForeignKey('User.User_id'), nullable=False)
    from_user_id = db.Column(db.Integer,db.ForeignKey('User.User_id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)