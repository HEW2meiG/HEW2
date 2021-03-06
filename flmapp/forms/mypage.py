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
from flmapp.models.token import UserTempToken
from flmapp.models.token import MailResetToken


class ProfileForm(FlaskForm):
    """プロフィール設定ページフォーム"""
    username = StringField('名前')
    usercode = StringField('ユーザーコード', render_kw={"pattern":"^[0-9A-Za-z]+$"})
    picture_path = FileField('アイコン画像を変更')
    prof_comment = TextAreaField('自己紹介')
    submit = SubmitField('変更する')

    def validate_usercode(self,field):
        if current_user.user_code != field.data and User.select_user_by_user_code(field.data):
            raise ValidationError('ユーザーコードはすでに使用されています。')


class ChangePasswordForm(FlaskForm):
    """パスワード・メール変更ページフォーム"""
    now_password = PasswordField('現在のパスワード ')
    email = StringField('メール ', validators=[Email('メールアドレスが誤っています')])
    password = PasswordField('パスワード', validators=[EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード確認:')
    submit = SubmitField('更新する')

    def validate_email(self, field):
        user = User.select_user_by_email(self.email.data)
        if user and user.User_id != int(current_user.get_id()):
            raise ValidationError('メールアドレスはすでに登録されています')
        if UserTempToken.email_exists(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')
        if MailResetToken.email_exists(field.data):
            raise ValidationError('メールアドレスはすでに登録されています')
        
    def validate_password(self, field):
        if not self.now_password.data == '':
            if self.password.data == '':
                raise ValidationError('新しいパスワードを入力してください')
        if not self.password.data == '':
            if len(field.data) < 8:
                raise ValidationError('パスワードは8文字以上です')
        
    def validate_now_password(self, field):
        if not self.password.data == '':
            if self.now_password.data == '':
                raise ValidationError('現在のパスワードを入力してください')
                

class IdentificationForm(FlaskForm):
    """本人情報更新ページフォーム"""
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
        validators=[DataRequired()])
    addr01 = StringField('市区町村',validators=[DataRequired()])
    addr02 = StringField('番地',validators=[DataRequired()])
    addr03 = StringField('建物名')
    submit = SubmitField('登録する')


class ShippingAddressForm(FlaskForm):
    """配送先住所選択フォーム"""
    ShippingAddress_id = RadioField('配送先住所', choices=[], coerce=int)
    submit = SubmitField('選択した住所に配送する')
    
    def validate(self):
        if not super(FlaskForm, self).validate():
            flash('配送先住所を選択してください。')
            return False
        if self.ShippingAddress_id.data is None:
            flash('配送先住所を選択してください。')
            return False
        return True


class ShippingAddressRegisterForm(FlaskForm):
    """配送先住所登録フォーム"""
    last_name = StringField('お名前(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)山田"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子"})
    last_name_kana = StringField('お名前カナ(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ"})
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
    is_default = BooleanField('デフォルトの配送先に設定する', render_kw={'checked': True})
    submit = SubmitField('登録する')


class ShippingAddressEditForm(FlaskForm):
    """配送先住所編集フォーム"""
    last_name = StringField('お名前(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)山田"})
    first_name = StringField('',validators=[DataRequired()],render_kw={"placeholder":"例)花子"})
    last_name_kana = StringField('お名前カナ(全角)',validators=[DataRequired()],render_kw={"placeholder":"例)ヤマダ"})
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
    submit = SubmitField('変更する')


class HiddenShippingAddressDeleteForm(FlaskForm):
    """配送先住所削除Hiddenフォーム"""
    ShippingAddress_id = HiddenField()
    submit = SubmitField('削除')


class PayWayForm(FlaskForm):
    """支払い方法選択フォーム"""
    pay_way = RadioField('支払い方法',choices=[(0,'代金引換')], coerce=int)
    submit = SubmitField('選択した支払い方法を使う')

class HiddenPayWayDeleteForm(FlaskForm):
    """支払い方法削除Hiddenフォーム"""
    Credit_id = HiddenField()
    submit = SubmitField('削除')


class CreditRegisterForm(FlaskForm):
    """クレジットカード情報登録ページフォーム"""
    credit_name = StringField('クレジットカード名義',validators=[DataRequired()])
    credit_num = IntegerField('クレジットカード番号 ',validators=[DataRequired()], render_kw={"placeholder":"半角数字のみ"})
    expiration_date01 = SelectField('有効期限',choices=[(1,'01'),(2,'02'),(3,'03'),(4,'04'),(5,'05'),(6,'06'),(7,'07'),(8,'08'),(9,'09'),\
        (10,'10'),(11,'11'),(12,'12')],validators=[DataRequired()],coerce=int)
    expiration_date02 = SelectField('',choices=[(2021,'21'),(2022,'22'),(2023,'23'),(2024,'24'),(2025,'25'),(2026,'26'),(2027,'27'),(2028,'28'),(2029,'29'),\
        (2030,'30'),(2031,'31')],validators=[DataRequired()],coerce=int)
    security_code = IntegerField('セキュリティコード', validators=[DataRequired()], render_kw={"placeholder":""})
    is_default = BooleanField('デフォルトの支払い方法に設定する', render_kw={'checked': True})
    submit = SubmitField('追加する')

    def validate_credit_num(self, field):
        if len(str(field.data)) != 16:
            raise ValidationError('クレジットカード番号が違います。')

    def validate_security_code(self, field):
        if len(str(field.data)) != 3 and len(str(field.data)) != 4:
            raise ValidationError('セキュリティコードが違います。')