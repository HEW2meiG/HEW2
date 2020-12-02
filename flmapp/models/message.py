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

    def create_new_PostMessage(self):
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

    def create_new_DealMessage(self):
        db.session.add(self)