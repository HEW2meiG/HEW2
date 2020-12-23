from flask import (
     Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell
)
from flmapp.models.reaction import (
    Likes, UserConnect
)
from flmapp.models.message import(
    PostMessage, DealMessage
)

bp = Blueprint('route', __name__, url_prefix='')


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)


@bp.route('/')
def home():
    """ホーム"""
    items = Sell.query.all()
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'home.html',
        items=items,
        liked_list=liked_list
    )


@bp.app_errorhandler(404)
def page_not_found(e):
    """ページが見つからない場合"""
    return redirect(url_for('route.home'))


@bp.app_errorhandler(500)
def server_error(e):
    """サーバーエラー"""
    return render_template('500.html'), 500