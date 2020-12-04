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

#購入情報Hiddenフォーム
class HiddenBuyForm(FlaskForm):
    pay_way = HiddenField()
    Credit_id = HiddenField()
    ShippingAddress_id = HiddenField()
    submit = SubmitField('購入確認画面へ')


#支払い方法選択フォーム
class PayWayForm(FlaskForm):
    pay_way = RadioField('支払い方法',choices=[('1','代金引換')])
    submit = SubmitField('選択した支払い方法を使う')

    def validate(self):
        if not super(Form, self).validate():
            return False
        # 支払い方法がクレジットカードで、クレジット情報IDがNULLのとき
        if self.pay_way.data == 2 & self.Credit_id.data is None:
            flash('クレジットカードが選択されていません。')
            return False
        return True