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

from flmapp.utils.recommendations import (
    recommend
)# レコメンド
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
        if form.n_d_submit.data or form.submit.data:
            items = Sell.item_search(search_word, sort, genre, value_min, value_max, status, postages, deal_statuses)
    return render_template('search/search.html', form=form, items=items, users=users, change_search=change_search)

# ユーザー検索処理
@bp.route('/user/', methods=['GET', 'POST'])
def user():
    form = SearchForm(request.args, meta={'csrf': False})
    items = None
    users = None
    change_search = 'user'
    # レコメンドリスト
    r_item_list = []
    r_user_list = []
    if current_user.is_authenticated:
        r_item_list,r_user_list = recommend(current_user.User_id)
    if request.method == 'GET':
        if form.submit.data:
            users = User.user_search_by_word(form.search.data)
    return render_template('search/search.html', form=form, items=items, users=users, change_search=change_search, r_user_list=r_user_list)
