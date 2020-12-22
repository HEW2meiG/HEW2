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
def shippingaddresses_processor():
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
        # Sell_idに紐づく全てのいいねレコード取得し、ログイン中のユーザーでフィルターをかける
        liked = Likes.get_like_by_sell_id_and_user_id(item.Sell_id)
        # likedが存在した場合
        if liked is not None:
            liked_list.append(item.Sell_id)
    return render_template(
        'home.html',
        items=items,
        liked_list=liked_list
    )


@bp.route('/like_ajax', methods=['POST'])
@login_required
def like_ajax():
    sell_id = request.form.get('sell_id', -1, type=int)
    liked = False
    like = Likes.get_like_by_sell_id_and_user_id(sell_id)
    # すでにいいねしていたら
    if like is not None:
        #いいねレコードから削除する
        with db.session.begin(subtransactions=True):
            Likes.delete_like(sell_id)
        db.session.commit()
    # いいねしていなければ
    else:
        # いいねテーブルに追加する。
        likes = Likes(
            Sell_id = sell_id,
            User_id = current_user.User_id
        )
        with db.session.begin(subtransactions=True):
            likes.create_new_likes()
        db.session.commit()
        liked = True
    all_likes = Likes.select_likes_by_sell_id(sell_id)
    return jsonify(item_id=sell_id, liked=liked, count=len(all_likes))


@bp.app_errorhandler(404)
def page_not_found(e):
    """ページが見つからない場合"""
    return redirect(url_for('route.home'))


@bp.app_errorhandler(500)
def server_error(e):
    """サーバーエラー"""
    return render_template('500.html'), 500