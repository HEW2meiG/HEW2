import os
import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User
)
from flmapp.forms.search import (
   SearchForm
)
from flmapp.models.trade import (
    Sell
)
from flmapp.models.reaction import (
    Likes
)

bp = Blueprint('search', __name__, url_prefix='/search')

# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)

# キーワード商品検索処理
@bp.route('/item/', methods=['GET'])
def item():
    form = SearchForm(request.args, meta={'csrf': False})
    items = None
    users = None
    change_search = 'item'
    if request.method == 'GET':
        search_word = form.search.data
        sort = form.sort.data
        genre = form.genre.data
        value_min = form.value_min.data
        value_max = form.value_max.data
        status = form.state.data
        postages = form.postage.data
        deal_statuses = form.sellstate.data
        if form.n_d_submit(value='絞り込んで検索') or form.submit.data(value='検索'):
            items = Sell.item_search(search_word, sort, genre, value_min, value_max, status, postages, deal_statuses)    
    return render_template('search/search.html', form=form, items=items, users=users, change_search=change_search)

# ユーザー検索処理
@bp.route('/user/', methods=['GET', 'POST'])
def user():
    form = SearchForm(request.args, meta={'csrf': False})
    items = None
    change_search = 'user'
    users = User.user_search_by_word(form.search.data)
    return render_template('search/search.html', form=form, items=items, users=users, change_search=change_search)
