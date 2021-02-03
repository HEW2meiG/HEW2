from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, SubmitField, SelectField,
    SelectMultipleField, IntegerField
)
from wtforms.validators import DataRequired
from wtforms import ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from flask_login import current_user
from flask import flash

from flmapp.models.user import User


class MultiCheckField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SearchForm(FlaskForm):
    """商品検索フォーム"""
    search = StringField('', validators=[DataRequired()])
    submit = SubmitField('検索')


class NarrowDownSearchForm(FlaskForm):
    """商品絞り込み検索フォーム"""
    sort = SelectField('',choices=[('並び変え','並び変え'),('価格の安い順','価格の安い順'),('価格の高い順','価格の高い順'),\
    ('出品の新しい順','出品の新しい順'),('いいね！の多い順','いいね！の多い順')]\
        )
    genre = SelectField('',choices=[('ジャンルを選択する','ジャンルを選択する'),('SF','SF'),('政治','政治'),('恋愛','恋愛'),\
    ('青春','青春'),('ミステリー','ミステリー'),('イヤミス','イヤミス'),('歴史','歴史'),\
    ('時代','時代'),('物語(短編)','物語(短編)'),('物語(中編)','物語(中編)'),('物語(長編)','物語(長編)')]\
        )
    value_min = IntegerField('')
    value_max = IntegerField('')
    state = MultiCheckField('',choices=[('すべて','すべて'),('新品、未使用','新品、未使用'),('未使用に近い','未使用に近い'),\
    ('目立った傷、汚れなし','目立った傷、汚れなし'),('やや傷や汚れあり','やや傷や汚れあり'),('傷や汚れあり','傷や汚れあり'),('全体的に状態が悪い','全体的に状態が悪い')]\
        )
    postage = MultiCheckField('',choices=[('すべて','すべて'),('発払い(出品者負担)','発払い(出品者負担)'),('着払い(購入者負担)','着払い(購入者負担)')]\
        )
    sellstate = MultiCheckField('',choices=[('すべて','すべて'),('販売中','販売中'),('売り切れ','売り切れ')]\
        )
    submit = SubmitField('絞り込んで検索')
    clean = SubmitField('クリア')

    def validate_value_min(self, field):
        if not self.value_max == '':
            if not self.value_min == '':
                raise ValidationError('最小金額を入力してください')
            
    def validate_value_max(self, field):
        if not self.value_min == '':
            if not self.value_max == '':
                raise ValidationError('最大金額を入力してください')