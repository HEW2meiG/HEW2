from wtforms.form import Form
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField,
    IntegerField,BooleanField,DateField,
    RadioField,SelectField,TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from flask import flash

from flmapp.models.auth import User

# ログイン用のForm
class LoginForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'パスワード: ',
        validators=[DataRequired(),
        EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード再入力: ', validators=[DataRequired()]
    )
    submit = SubmitField('ログイン')

# 登録用のForm
class RegisterForm(Form):
    picture_path = FileField('アイコン画像を設定')
    email = StringField(
        'メール',render_kw={"placeholder":"PC・携帯どちらでも可"},validators=[DataRequired(), Email('メールアドレスが誤っています')]
    )
    username = StringField('ユーザーネーム', validators=[DataRequired()],render_kw={"placeholder":"例)ポチ"})
    last_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)山田"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子"})
    last_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ"})
    first_name_kana = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)ハナコ"})
    birth = DateField('生年月日',format='%Y/%m/%d',render_kw={"placeholder":"例)1999/08/30"})
    zip01 = StringField('郵便番号(ハイフンなし)',validators=[DataRequired()],render_kw={"placeholder":"例)123456"})
    pref01 = StringField('都道府県',validators=[DataRequired()])
    addr01 = StringField('市区町村',validators=[DataRequired()])
    addr02 = StringField('番地',validators=[DataRequired()])
    addr03 = StringField('建物名')

    
    submit = SubmitField('登録する')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')

# パスワード設定用のフォーム
class ResetPasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードを更新する')
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')

class ForgotPasswordForm(Form):
    email = StringField('メール: ', validators=[DataRequired(), Email()])
    submit = SubmitField('パスワードを再設定する')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data):
            raise ValidationError('そのメールアドレスは存在しません')


class UserForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')]
    )
    username = StringField('名前: ', validators=[DataRequired()])
    picture_path = FileField('ファイルアップロード')
    submit = SubmitField('登録情報更新')

    def validate(self):
        if not super(Form, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('そのメールアドレスはすでに登録されています')
                return False
        return True

class ChangePasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード確認: ', validators=[DataRequired()]
    )
    submit = SubmitField('パスワードの更新')
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上です')
