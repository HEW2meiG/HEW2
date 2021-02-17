from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_required, current_user
)
from flmapp import db
from functools import wraps # カスタムデコレーターに使用

from flmapp.utils.recommendations import (
    topMatches, getRecommendations
)
from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell
)
from flmapp.models.reaction import (
    Likes, UserConnect
)


bp = Blueprint('ajax', __name__, url_prefix='')


def ajax_login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            not_authenticated = True
            return jsonify(not_authenticated=not_authenticated)
    return decorated_function


@bp.route('/like_ajax', methods=['POST'])
@ajax_login_required
def like_ajax():
    """いいね機能ajax処理"""
    sell_id = request.form.get('sell_id', -1, type=int)
    if sell_id != -1:
        liked = False
        like = Likes.liked_exists(sell_id)
        # レコメンドキャッシュのクリア
        # 読み込み速度の問題によりデモではキャッシュクリアを行わない
        # getRecommendations.cache_clear()
        # topMatches.cache_clear()
        # すでにいいねしていたら
        if like:
            #いいねテーブルから削除する
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
        # Sell_idが一致するいいねレコードを抽出 len()で要素数を代入
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return jsonify(item_id=sell_id, liked=liked, count=len(all_likes))


@bp.route('/follow_ajax', methods=['POST'])
@ajax_login_required
def follow_ajax():
    """フォロー機能ajax処理"""
    user_id = request.form.get('user_id', -1, type=int)
    if user_id != -1:
        followed = False
        follow = UserConnect.followed_exists(user_id)
        # レコメンドキャッシュのクリア
        topMatches.cache_clear()
        # すでにフォローしていたら
        if follow:
            #フォローテーブルから削除する
            with db.session.begin(subtransactions=True):
                UserConnect.delete_follow(user_id)
            db.session.commit()
        # フォローしていなければ
        else:
            # フォローテーブルに追加する。
            userconnect = UserConnect(
                to_user_id = user_id,
                from_user_id = current_user.User_id
            )
            with db.session.begin(subtransactions=True):
                userconnect.create_new_userconnect()
            db.session.commit()
            followed = True
        # User_idがto_user_idと一致するフォローレコードを抽出 len()で要素数を代入
        all_followers = UserConnect.select_followers_by_user_id(user_id)
        return jsonify(user_id=user_id, followed=followed, count=len(all_followers))