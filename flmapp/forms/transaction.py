from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField,
    IntegerField,BooleanField,DateField,
    RadioField,SelectField,TextAreaField,
)
from wtforms.validators import DataRequired, EqualTo, NumberRange
from wtforms import ValidationError
from flask_login import current_user
from flask import flash

from flmapp.utils.button import ButtonField


class DealMessageForm(FlaskForm):
    """取引メッセージフォーム"""
    message = TextAreaField(render_kw={"placeholder":"メッセージを送る"})
    submit = ButtonField('<i class="fas fa-paper-plane"></i>')


class NoticeRatingForm(FlaskForm):
    """通知・評価フォーム"""
    notice_condition = HiddenField()
    notice_flg = BooleanField()
    rating = RadioField('評価',choices=[(1,'良い'),(2,'悪い')], default=1, coerce=int)
    rating_message = TextAreaField(render_kw={"placeholder":"この度はお取引ありがとうございました。"})
    submit = SubmitField()

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        if self.notice_condition.data == 'has_sent':
            if self.notice_flg.data == False:
                flash('※発送通知にチェックしてください。')
                return False
        if self.notice_condition.data == 'has_got':
            if self.notice_flg.data == False:
                flash('※受け取り確認にチェックしてください。')
                return False
        return True