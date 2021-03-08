from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField,
    IntegerField,BooleanField,DateField,
    RadioField,SelectField,TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from flask import flash
import flask_session_captcha

from flmapp.models.user import User
from flmapp.models.token import UserTempToken
from flmapp.models.token import MailResetToken

class LoginForm(FlaskForm):
    email = StringField(
        'メールアドレス',render_kw={"placeholder":"koshokaikou@mail.com"}, validators=[DataRequired('入力してください。'), Email('メールアドレスが間違っています。')]
    )
    password = PasswordField('パスワード', validators=[DataRequired('入力してください。')])
    captcha = StringField('画像に表示されている文字を入力してください。')
    submit = SubmitField('ログイン')

    def validate_captcha(self, field):
        if flask_session_captcha.session.get('captcha_answer') != field.data:
            raise ValidationError('画像に表示されている文字と違います。')


class CreateUserForm(FlaskForm):
    email = StringField(
        'メールアドレス',render_kw={"placeholder":"koshokaikou@mail.com"},validators=[DataRequired(), Email('@ぬけてんで。')]
    )
    submit = SubmitField('メールを送信する')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています。')
        if UserTempToken.email_exists(field.data):
            raise ValidationError('メールアドレスはすでに登録されています。')
        if MailResetToken.email_exists(field.data):
            raise ValidationError('メールアドレスはすでに登録されています。')


class RegisterForm(FlaskForm):
    password = PasswordField(
        'パスワード',
        validators=[DataRequired('入力してください。'), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード確認', validators=[DataRequired('入力してください。')]
    )
    picture_path = FileField('アイコン画像を設定')
    username = StringField('ユーザーネーム', validators=[DataRequired()],render_kw={"placeholder":"例)ポチ"})
    user_code = StringField('ユーザーコード', validators=[DataRequired()],render_kw={"placeholder":"pochi0830", "pattern":"^[0-9A-Za-z]+$"})
    last_name = StringField('お名前(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)山田", "pattern": "[^A-Za-z0-9０-９]+"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子", "pattern": "[^A-Za-z0-9０-９]+"})
    last_name_kana = StringField('お名前カナ(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ", "pattern":"(?=.*?[\u30A1-\u30FC])[\u30A1-\u30FC\s]*"})
    first_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ハナコ", "pattern":"(?=.*?[\u30A1-\u30FC])[\u30A1-\u30FC\s]*"})
    b_year = SelectField('生年月日', choices=[(0,'--')],validators=[DataRequired()], coerce=int)
    b_month = SelectField('', choices=[(0,'--')],validators=[DataRequired()], coerce=int)
    b_date = SelectField('', choices=[(0,'--')], validators=[DataRequired()], coerce=int)
    zip01 = StringField('郵便番号(ハイフンなし)',validators=[DataRequired()],render_kw={"placeholder":"例)123456", "pattern":"\d{7}"})
    pref01 = SelectField('都道府県',choices=[('','未選択'),('北海道','北海道'),('青森県','青森県'),('岩手県','岩手県'),('宮城県','宮城県'),('秋田県','秋田県'),\
        ('山形県','山形県'),('福島県','福島県'),('茨城県','茨城県'),('栃木県','栃木県'),('群馬県','群馬県'),('埼玉県','埼玉県'),('千葉県','千葉県'),\
        ('東京都','東京都'),('神奈川県','神奈川県'),('新潟県','新潟県'),('富山県','富山県'),('石川県','石川県'),('福井県','福井県'),('山梨県','山梨県'),\
        ('長野県','長野県'),('岐阜県','岐阜県'),('静岡県','静岡県'),('愛知県','愛知県'),('三重県','三重県'),('滋賀県','滋賀県'),('京都府','京都府'),\
        ('大阪府','大阪府'),('兵庫県','兵庫県'),('奈良県','奈良県'),('和歌山県','和歌山県'),('鳥取県','鳥取県'),('島根県','島根県'),('岡山県','岡山県'),\
        ('広島県','広島県'),('山口県','山口県'),('徳島県','徳島県'),('香川県','香川県'),('愛媛県','愛媛県'),('高知県','高知県'),('福岡県','福岡県'),\
        ('佐賀県','佐賀県'),('長崎県','長崎県'),('熊本県','熊本県'),('大分県','大分県'),('宮崎県','宮崎県'),('鹿児島県','鹿児島県'),('沖縄県','沖縄県')],\
        validators=[DataRequired('入力してください。')])
    addr01 = StringField('市区町村',validators=[DataRequired('入力してください。')])
    addr02 = StringField('番地',validators=[DataRequired('入力してください。')])
    addr03 = StringField('建物名')
    captcha = StringField('画像に表示されている文字を入力してください。')
    submit = SubmitField('登録する')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

    def validate_user_code(self, field):
        if User.select_user_by_user_code(field.data):
            raise ValidationError('このユーザーコードはすでに使用されています')

    def validate_captcha(self, field):
        if flask_session_captcha.session.get('captcha_answer') != field.data:
            raise ValidationError('画像に表示されている文字と違います。')


class ForgotPasswordForm(FlaskForm):
    email = StringField('メールアドレス',render_kw={"placeholder":"koshokaikou@mail.com"}, validators=[DataRequired(), Email('@ぬけてんで。')])
    submit = SubmitField('メールを送信する')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data):
            raise ValidationError('そのメールアドレスは存在しません')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        '新しいパスワード',
        validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        '新しいパスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードを更新する')
    
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')