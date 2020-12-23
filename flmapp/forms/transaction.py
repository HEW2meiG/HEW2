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


class DealMessageForm(FlaskForm):
    """取引メッセージフォーム"""
    message = TextAreaField()
    submit = SubmitField('送信')