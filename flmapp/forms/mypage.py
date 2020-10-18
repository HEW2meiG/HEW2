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

# プロフィール設定ページフォーム
class ProfileForm(Form):
    username = StringField('名前:')
    picture_path = FileField('アイコン画像を変更')
    prof_comment = TextAreaField('自己紹介:')
    submit = SubmitField('変更する')

# パスワード・メール変更ページフォーム
class ChangePasswordForm(Form):
    email = StringField('メール: ', validators=[Email('メールアドレスが誤っています')])
    password = PasswordField(
        'パスワード',
        validators=[EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField('パスワード確認:')
    submit = SubmitField('更新する')

    def validate(self):
        if not super(Form, self).validate():
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