from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField,
    IntegerField,BooleanField,DateField,
    RadioField,SelectField,TextAreaField,
)
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, EqualTo, NumberRange
from wtforms import ValidationError
from flask_login import current_user
from flask import flash


class SellForm(FlaskForm):
    """出品情報フォーム"""
    sell_title = StringField('本のタイトル', validators=[DataRequired()])
    key1 = StringField('本のキーワード1', validators=[DataRequired()])
    key2 = StringField('本のキーワード2', validators=[DataRequired()])
    key3 = StringField('本のキーワード3', validators=[DataRequired()])
    sell_comment = TextAreaField('出品する本のコメント', validators=[DataRequired()])
    price = IntegerField('販売価格', validators=[DataRequired(), NumberRange(300, 99999, '300円から99,999円までの値段を入力してください。')])
    item_picture_path = FileField('商品の画像を設定',validators=[FileRequired('画像を選択してください')])
    genre = SelectField('ジャンル', choices=[('','選択してください'), ('SF', 'SF'), ('政治', '政治'),\
        ('恋愛', '恋愛'), ('青春', '青春'),  ('ミステリー', 'ミステリー'), ('イヤミス', 'イヤミス'),\
        ('歴史', '歴史'), ('時代', '時代'), ('物語(短編)', '物語(短編)'), ('物語(中編)', '物語(中編)'),\
        ('物語(長編)', '物語(長編)')],\
        validators=[DataRequired()]
    )
    item_state = SelectField('商品の状態', choices=[('','選択してください'), ('新品', '新品'),\
        ('未使用に近い', '未使用に近い'), ('目立った傷や汚れなし', '目立った傷や汚れなし'),  ('やや傷や汚れあり', 'やや傷や汚れあり'),\
        ('傷や汚れあり', '傷や汚れあり'), ('全体的に状態が悪い', '全体的に状態が悪い')],\
        validators=[DataRequired()]
    )
    postage = SelectField('配送料の負担', choices=[('','選択してください'), ('送料込み(出品者負担)', '送料込み(出品者負担)'),('着払い(購入者負担)', '着払い(購入者負担)')],\
        validators=[DataRequired()]
    )    
    send_way = SelectField('配送の方法', choices=[('','選択してください'), ('未定', '未定'),\
        ('ゆうメール', 'ゆうメール'), ('レターパック', 'レターパック'),  ('クロネコヤマト', 'クロネコヤマト'),\
        ('ゆうパック', 'ゆうパック'), ('クリックポスト', 'クリックポスト'), ('ゆうパケット', 'ゆうパケット')],\
        validators=[DataRequired()]
    )
    consignor = SelectField('配送元地域',choices=[('','選択してください'),('北海道','北海道'),('青森県','青森県'),('岩手県','岩手県'),('宮城県','宮城県'),('秋田県','秋田県'),\
        ('山形県','山形県'),('福島県','福島県'),('茨城県','茨城県'),('栃木県','栃木県'),('群馬県','群馬県'),('埼玉県','埼玉県'),('千葉県','千葉県'),\
        ('東京都','東京都'),('神奈川県','神奈川県'),('新潟県','新潟県'),('富山県','富山県'),('石川県','石川県'),('福井県','福井県'),('山梨県','山梨県'),\
        ('長野県','長野県'),('岐阜県','岐阜県'),('静岡県','静岡県'),('愛知県','愛知県'),('三重県','三重県'),('滋賀県','滋賀県'),('京都府','京都府'),\
        ('大阪府','大阪府'),('兵庫県','兵庫県'),('奈良県','奈良県'),('和歌山県','和歌山県'),('鳥取県','鳥取県'),('島根県','島根県'),('岡山県','岡山県'),\
        ('広島県','広島県'),('山口県','山口県'),('徳島県','徳島県'),('香川県','香川県'),('愛媛県','愛媛県'),('高知県','高知県'),('福岡県','福岡県'),\
        ('佐賀県','佐賀県'),('長崎県','長崎県'),('熊本県','熊本県'),('大分県','大分県'),('宮崎県','宮崎県'),('鹿児島県','鹿児島県'),('沖縄県','沖縄県')],\
        validators=[DataRequired()]
    )
    schedule = SelectField('発送日の目安', choices=[('','選択してください'), ('1日から2日で発送', '1日から2日で発送'),\
        ('2日から3日で発送', '2日から3日で発送'), ('4日から7日で発送', '4日から7日で発送')],\
        validators=[DataRequired()]
    )
    remarks = TextAreaField('備考')
    submit = SubmitField('出品確認画面へ')


class HiddenSellForm(FlaskForm):
    """出品情報Hiddenフォーム"""
    sell_title = HiddenField()
    key1 = HiddenField()
    key2 = HiddenField()
    key3 = HiddenField()
    sell_comment = HiddenField()
    price = HiddenField()
    item_picture_path = HiddenField()
    genre = HiddenField()
    item_state = HiddenField()
    postage = HiddenField()   
    send_way = HiddenField()
    consignor = HiddenField()
    schedule = HiddenField()
    remarks = HiddenField()
    submit = SubmitField()


class SellUpdateForm(FlaskForm):
    """出品情報更新フォーム"""
    sell_title = StringField('本のタイトル', validators=[DataRequired()])
    key1 = StringField('本のキーワード1', validators=[DataRequired()])
    key2 = StringField('本のキーワード2', validators=[DataRequired()])
    key3 = StringField('本のキーワード3', validators=[DataRequired()])
    sell_comment = TextAreaField('出品する本のコメント', validators=[DataRequired()])
    price = IntegerField('販売価格', validators=[DataRequired(), NumberRange(300, 99999, '300円から99,999円までの値段を入力してください。')])
    item_picture_path = FileField('商品の画像を設定')
    genre = SelectField('ジャンル', choices=[('','選択してください'), ('SF', 'SF'), ('政治', '政治'),\
        ('恋愛', '恋愛'), ('青春', '青春'),  ('ミステリー', 'ミステリー'), ('イヤミス', 'イヤミス'),\
        ('歴史', '歴史'), ('時代', '時代'), ('物語(短編)', '物語(短編)'), ('物語(中編)', '物語(中編)'),\
        ('物語(長編)', '物語(長編)')],\
        validators=[DataRequired()]
    )
    item_state = SelectField('商品の状態', choices=[('','選択してください'), ('新品', '新品'),\
        ('未使用に近い', '未使用に近い'), ('目立った傷や汚れなし', '目立った傷や汚れなし'),  ('やや傷や汚れあり', 'やや傷や汚れあり'),\
        ('傷や汚れあり', '傷や汚れあり'), ('全体的に状態が悪い', '全体的に状態が悪い')],\
        validators=[DataRequired()]
    )
    postage = SelectField('配送料の負担', choices=[('','選択してください'), ('送料込み(出品者負担)', '送料込み(出品者負担)'),('着払い(購入者負担)', '着払い(購入者負担)')],\
        validators=[DataRequired()]
    )    
    send_way = SelectField('配送の方法', choices=[('','選択してください'), ('未定', '未定'),\
        ('ゆうメール', 'ゆうメール'), ('レターパック', 'レターパック'),  ('クロネコヤマト', 'クロネコヤマト'),\
        ('ゆうパック', 'ゆうパック'), ('クリックポスト', 'クリックポスト'), ('ゆうパケット', 'ゆうパケット')],\
        validators=[DataRequired()]
    )
    consignor = SelectField('配送元地域',choices=[('','選択してください'),('北海道','北海道'),('青森県','青森県'),('岩手県','岩手県'),('宮城県','宮城県'),('秋田県','秋田県'),\
        ('山形県','山形県'),('福島県','福島県'),('茨城県','茨城県'),('栃木県','栃木県'),('群馬県','群馬県'),('埼玉県','埼玉県'),('千葉県','千葉県'),\
        ('東京都','東京都'),('神奈川県','神奈川県'),('新潟県','新潟県'),('富山県','富山県'),('石川県','石川県'),('福井県','福井県'),('山梨県','山梨県'),\
        ('長野県','長野県'),('岐阜県','岐阜県'),('静岡県','静岡県'),('愛知県','愛知県'),('三重県','三重県'),('滋賀県','滋賀県'),('京都府','京都府'),\
        ('大阪府','大阪府'),('兵庫県','兵庫県'),('奈良県','奈良県'),('和歌山県','和歌山県'),('鳥取県','鳥取県'),('島根県','島根県'),('岡山県','岡山県'),\
        ('広島県','広島県'),('山口県','山口県'),('徳島県','徳島県'),('香川県','香川県'),('愛媛県','愛媛県'),('高知県','高知県'),('福岡県','福岡県'),\
        ('佐賀県','佐賀県'),('長崎県','長崎県'),('熊本県','熊本県'),('大分県','大分県'),('宮崎県','宮崎県'),('鹿児島県','鹿児島県'),('沖縄県','沖縄県')],\
        validators=[DataRequired()]
    )
    schedule = SelectField('発送日の目安', choices=[('','選択してください'), ('1日から2日で発送', '1日から2日で発送'),\
        ('2日から3日で発送', '2日から3日で発送'), ('4日から7日で発送', '4日から7日で発送')],\
        validators=[DataRequired()]
    )
    remarks = TextAreaField('備考')
    submit = SubmitField('更新する')
    
class SellUpdateFlgAndDeleteForm(FlaskForm):
    """出品フラグ更新・出品削除フォーム"""
    Sell_id = HiddenField()
    submit = SubmitField()