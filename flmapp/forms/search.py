from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, SubmitField, SelectField,
    SelectMultipleField, HiddenField, IntegerField, RadioField
)
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from flask_login import current_user
from flask import flash

from flmapp.utils.button import ButtonField
from flmapp.models.user import User


class MultiCheckField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SearchForm(FlaskForm):
    """商品検索フォーム"""
    search = StringField('')
    submit = ButtonField('<i class="fas fa-search"></i>')
    sort = SelectField('',choices=[('','並び変え'),('価格の安い順','価格の安い順'),('価格の高い順','価格の高い順'),\
    ('出品の新しい順','出品の新しい順'),('いいね！の多い順','いいね！の多い順')]\
        )
    genre = SelectField('',choices=[('all','すべて'),('SF','SF'),('政治','政治'),('恋愛','恋愛'),\
    ('青春','青春'),('ミステリー','ミステリー'),('イヤミス','イヤミス'),('歴史','歴史'),\
    ('時代','時代'),('物語(短編)','物語(短編)'),('物語(中編)','物語(中編)'),('物語(長編)','物語(長編)')]\
        )
    value_min = IntegerField('',render_kw={"placeholder":"¥Min"})
    value_max = IntegerField('',render_kw={"placeholder":"¥Max"})
    state = MultiCheckField('',choices=[('新品','新品'),('未使用に近い','未使用に近い'),\
    ('目立った傷や汚れなし','目立った傷や汚れなし'),('やや傷や汚れあり','やや傷や汚れあり'),('傷や汚れあり','傷や汚れあり'),('全体的に状態が悪い','全体的に状態が悪い')]\
        )
    postage = MultiCheckField('',choices=[('送料込み(出品者負担)','送料込み(出品者負担)'),('着払い(購入者負担)','着払い(購入者負担)')]\
        )
    sellstate = MultiCheckField('',choices=[('販売中','販売中'),('売り切れ','売り切れ')]\
        )
    n_d_submit = SubmitField('絞り込んで検索')
