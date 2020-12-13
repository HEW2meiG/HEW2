from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField,
    HiddenField, IntegerField, BooleanField, DateField,
    RadioField, SelectField, TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from flask import flash

from flmapp.models.user import User


class ProfileForm(FlaskForm):
    """プロフィール設定ページフォーム"""
    username = StringField('名前:')
    picture_path = FileField('アイコン画像を変更')
    prof_comment = TextAreaField('自己紹介:')
    submit = SubmitField('変更する')


class ChangePasswordForm(FlaskForm):
    """パスワード・メール変更ページフォーム"""
    email = StringField('メール: ', validators=[Email('メールアドレスが誤っています')])
    password = PasswordField(
        'パスワード',
        validators=[EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField('パスワード確認:')
    submit = SubmitField('更新する')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.User_id != int(current_user.get_id()):
                flash('そのメールアドレスはすでに登録されています')
                return False
        return True

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')


class IdentificationForm(FlaskForm):
    """本人情報更新ページフォーム"""
    last_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)山田"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子"})
    last_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ"})
    first_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ハナコ"})
    birth = DateField('生年月日',format='%Y/%m/%d',render_kw={"placeholder":"例)1999/08/30"})
    zip01 = StringField('郵便番号(ハイフンなし)',validators=[DataRequired()],render_kw={"placeholder":"例)123456"})
    pref01 = SelectField('都道府県',choices=[('','未選択'),('北海道','北海道'),('青森県','青森県'),('岩手県','岩手県'),('宮城県','宮城県'),('秋田県','秋田県'),\
        ('山形県','山形県'),('福島県','福島県'),('茨城県','茨城県'),('栃木県','栃木県'),('群馬県','群馬県'),('埼玉県','埼玉県'),('千葉県','千葉県'),\
        ('東京都','東京都'),('神奈川県','神奈川県'),('新潟県','新潟県'),('富山県','富山県'),('石川県','石川県'),('福井県','福井県'),('山梨県','山梨県'),\
        ('長野県','長野県'),('岐阜県','岐阜県'),('静岡県','静岡県'),('愛知県','愛知県'),('三重県','三重県'),('滋賀県','滋賀県'),('京都府','京都府'),\
        ('大阪府','大阪府'),('兵庫県','兵庫県'),('奈良県','奈良県'),('和歌山県','和歌山県'),('鳥取県','鳥取県'),('島根県','島根県'),('岡山県','岡山県'),\
        ('広島県','広島県'),('山口県','山口県'),('徳島県','徳島県'),('香川県','香川県'),('愛媛県','愛媛県'),('高知県','高知県'),('福岡県','福岡県'),\
        ('佐賀県','佐賀県'),('長崎県','長崎県'),('熊本県','熊本県'),('大分県','大分県'),('宮崎県','宮崎県'),('鹿児島県','鹿児島県'),('沖縄県','沖縄県')],\
        validators=[DataRequired()])
    addr01 = StringField('市区町村',validators=[DataRequired()])
    addr02 = StringField('番地',validators=[DataRequired()])
    addr03 = StringField('建物名')
    submit = SubmitField('登録する')


class ShippingAddressForm(FlaskForm):
    """配送先住所ページフォーム"""
    last_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)山田"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子"})
    last_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ"})
    first_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ハナコ"})
    zip01 = StringField('郵便番号(ハイフンなし)',validators=[DataRequired()],render_kw={"placeholder":"例)123456"})
    pref01 = SelectField('都道府県',choices=[('','未選択'),('北海道','北海道'),('青森県','青森県'),('岩手県','岩手県'),('宮城県','宮城県'),('秋田県','秋田県'),\
        ('山形県','山形県'),('福島県','福島県'),('茨城県','茨城県'),('栃木県','栃木県'),('群馬県','群馬県'),('埼玉県','埼玉県'),('千葉県','千葉県'),\
        ('東京都','東京都'),('神奈川県','神奈川県'),('新潟県','新潟県'),('富山県','富山県'),('石川県','石川県'),('福井県','福井県'),('山梨県','山梨県'),\
        ('長野県','長野県'),('岐阜県','岐阜県'),('静岡県','静岡県'),('愛知県','愛知県'),('三重県','三重県'),('滋賀県','滋賀県'),('京都府','京都府'),\
        ('大阪府','大阪府'),('兵庫県','兵庫県'),('奈良県','奈良県'),('和歌山県','和歌山県'),('鳥取県','鳥取県'),('島根県','島根県'),('岡山県','岡山県'),\
        ('広島県','広島県'),('山口県','山口県'),('徳島県','徳島県'),('香川県','香川県'),('愛媛県','愛媛県'),('高知県','高知県'),('福岡県','福岡県'),\
        ('佐賀県','佐賀県'),('長崎県','長崎県'),('熊本県','熊本県'),('大分県','大分県'),('宮崎県','宮崎県'),('鹿児島県','鹿児島県'),('沖縄県','沖縄県')],\
        validators=[DataRequired()])
    addr01 = StringField('市区町村',validators=[DataRequired()])
    addr02 = StringField('番地',validators=[DataRequired()])
    addr03 = StringField('建物名')
    submit = SubmitField('登録する')


class PayWayForm(FlaskForm):
    """支払い方法選択フォーム"""
    pay_way = RadioField('支払い方法',choices=[(0,'代金引換')], coerce=int)
    submit = SubmitField('選択した支払い方法を使う')


class CreditRegisterForm(FlaskForm):
    """クレジットカード情報登録ページフォーム"""
    credit_name = StringField('クレジットカード名義',validators=[DataRequired()])
    credit_num = IntegerField('クレジットカード番号 ',validators=[DataRequired()], render_kw={"placeholder":"半角数字のみ"})
    expiration_date01 = SelectField('',choices=[(1,'01'),(2,'02'),(3,'03'),(4,'04'),(5,'05'),(6,'06'),(7,'07'),(8,'08'),(9,'09'),\
        (10,'10'),(11,'11'),(12,'12')],validators=[DataRequired()],coerce=int)
    expiration_date02 = SelectField('',choices=[(2021,'21'),(2022,'22'),(2023,'23'),(2024,'24'),(2025,'25'),(2026,'26'),(2027,'27'),(2028,'28'),(2029,'29'),\
        (2030,'30'),(2031,'31')],validators=[DataRequired()],coerce=int)
    security_code = IntegerField('セキュリティコード: ', validators=[DataRequired()], render_kw={"placeholder":"カード背面4桁もしくは3桁の番号"})
    is_default = BooleanField('デフォルトの支払い方法に設定する', render_kw={'checked': True})
    submit = SubmitField('追加する')

    def validate_credit_num(self, field):
        if len(str(field.data)) != 16:
            raise ValidationError('クレジットカード番号が違います。')

    def validate_security_code(self, field):
        if len(str(field.data)) != 3 and len(str(field.data)) != 4:
            raise ValidationError('セキュリティコードが違います。')