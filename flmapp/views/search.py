# bp = Blueprint('search', __name__, url_prefix='/search)
import os
import glob # 画像のリサイズ
import datetime
from PIL import Image # 画像のリサイズ
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,
    current_app as app #Blueprint環境下で、設定値(config)を取得
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.utils.image_square import (
    crop_max_square
)
from flmapp.models.user import (
    User, UserInfo, Address, ShippingAddress, Credit
)
from flmapp.models.token import (
    PasswordResetToken, MailResetToken
)
from flmapp.forms.search import (
   SearchForm, NarrowDownSearchForm
)
from flmapp.models.trade import (
    Sell, Genre, Item_state, Postage, Send_way, Schedule, Deal_status
)
from flmapp.models.reaction import (
    Likes
)

from flmapp import mail # メール送信インポート
from flask_mail import Mail, Message # メール送信インポート

bp = Blueprint('search', __name__, url_prefix='/search')
# bp = Blueprint('mypage', __name__, url_prefix='/mypage')

# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)

# キーワード商品・ユーザー検索処理
@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    ndform = NarrowDownSearchForm(request.form)
    items = None
    search_word = None
    change_search = 'ITEM'
    if request.method == 'POST' and form.validate():
        search_word = form.search.data
        if change_search == 'ITEM':
            items = Sell.item_search_by_word(search_word)
        elif change_search == 'USER':
            items = User.user_search_by_word(search_word)
    return render_template('search/search.html', form=form, ndform=ndform, items=items, search_word=search_word, change_search=change_search)

# キーワード商品・ユーザー検索選択処理
@bp.route('/change_search/<search_word>/<change_search>')
def change_search(search_word, change_search):
    form = SearchForm(request.form)
    ndform = NarrowDownSearchForm(request.form)
    items = None
    if not search_word == ' ':
        if change_search == 'ITEM':
            items = Sell.item_search_by_word(search_word)
        elif change_search == 'USER':
            items = User.user_search_by_word(search_word)
    else:
        search_word = ''
        if change_search == 'ITEM':
            items = Sell.item_search_by_word(search_word)
        elif change_search == 'USER':
            items = User.user_search_by_word(search_word)
    return render_template('search/search.html', form=form, ndform=ndform, items=items, search_word=search_word, change_search=change_search)

# 絞り込み商品検索処理
@bp.route('/narrow_down_search', methods=['GET', 'POST'])
def narrow_down_search():
    form = SearchForm(request.form)
    ndform = NarrowDownSearchForm(request.form)
    items = None
    search_word = ''
    change_search = 'ITEM'
    nditems = []
    search_query = ""
    sort = None
    genre = None
    value_min = 0
    value_max = 99999
    state = None
    postage = None
    sellstate = None
    if request.method == 'POST' and ndform.validate():
        search_word = ndform.search_word.data
        sort = ndform.sort.data
        if search_word:
            search_word = ''
        if sort == '並び変え':
            items = Sell.item_search_by_word(search_word)
        else:
            items = Sell.item_search_by_sort(search_word, sort)
        genre = ndform.genre.data
        value_min = ndform.value_min.data
        value_max = ndform.value_max.data
        states = request.form.getlist('state')
        postages = request.form.getlist('postage')
        sellstates = request.form.getlist('sellstate')
        if items:
            # ジャンル
            if not genre == 'ジャンルを選択する':
                for item in items:
                    if item.genre.name == genre:
                        nditems += [item]
                items = nditems
                nditems = []
            # 値段
            for item in items:
                if item.price >= value_min and item.price <= value_max:
                    nditems += [item]
            items = nditems
            nditems = []
            # 商品の状態
            if not states == []:
                for item in items:
                    for state in states:
                        if item.item_state.name == state:
                            nditems += [item]
                items = nditems
                nditems = []
            # 配送料の負担
            if not postages == []:
                for item in items:
                    for postage in postages:
                        if item.postage.name == postage:
                            nditems += [item]
                items = nditems
                nditems = []
            # 販売状況
            if not sellstates == []:
                for item in items:
                    for sellstate in sellstates:
                        if sellstate == '販売中':
                            if item.deal_status.name == '出品中':
                                nditems += [item]
                        elif sellstate == '売り切れ':
                            if item.deal_status.name == '取引中' or item.deal_status.name == '取引済み':
                                nditems += [item]
                items = nditems
                nditems = []

    return render_template('search/search.html', form=form, ndform=ndform, items=items, search_word=search_word, change_search=change_search)
