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

#購入情報フォーム
class BuyForm(FlaskForm):
    pay_way = RadioField('支払い方法',choices=[('0','代金引換')])
    submit = SubmitField()