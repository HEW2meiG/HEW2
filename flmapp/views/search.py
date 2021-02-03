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
    Sell
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

# キーワード検索処理
@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    ndform = NarrowDownSearchForm(request.form)
    items = None
    if request.method == 'POST' and form.validate():
        searchword = form.search.data
        items = Sell.search_by_word(searchword)
    return render_template('search/search.html', form=form, ndform=ndform, items=items)

# 絞り込み検索処理
@bp.route('/search', methods=['GET', 'POST'])
def narrow_down_search(word):
    form = SearchForm(request.form)
    ndform = NarrowDownSearchForm(request.form)
    items = None
    if request.method == 'POST' and form.validate():
        items = None
    return render_template('search/search.html', form=form, ndform=ndform, items=items)
