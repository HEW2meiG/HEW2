from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_required, current_user
)
from flmapp import db

from flmapp.models.user import (
    User
)
from flmapp.models.reaction import (
    UserConnect, Likes
)
from flmapp.models.trade import (
    Rating, Sell
)


bp = Blueprint('user', __name__, url_prefix='/user')


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)

# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def followers_count_processor():
    def followers_count(user_id):
        """フォロワーの数をカウントして返す"""
        all_followers = UserConnect.select_followers_by_user_id(user_id)
        return len(all_followers)
    return dict(followers_count=followers_count)


@bp.route('/userdata/<string:user_code>', methods=['GET', 'POST'])
def userdata(user_code):
    user = User.select_user_by_user_code(user_code)
    if user is None:
        return redirect(url_for('route.home'))
    # ログイン中のユーザーがユーザーページのユーザーをフォローしているかの判定
    followed = UserConnect.followed_exists(user.User_id)
    follows = UserConnect.select_follows_by_user_id(user.User_id)
    good_ratings_count,bad_ratings_count = Rating.select_rate_by_user_id(user.User_id)
    # ユーザーが出品した商品
    items = Sell.select_sell_by_user_id(user.User_id)
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'user/userdata.html', user=user, followed=followed, follows_count=len(follows),
        good_ratings_count=good_ratings_count, bad_ratings_count=bad_ratings_count,
        items=items, liked_list=liked_list
    )

@bp.route('/userdata/<string:user_code>/likes', methods=['GET', 'POST'])
def userdata_likes(user_code):
    user = User.select_user_by_user_code(user_code)
    if user is None:
        return redirect(url_for('route.home'))
    # ログイン中のユーザーがユーザーページのユーザーをフォローしているかの判定
    followed = UserConnect.followed_exists(user.User_id)
    follows = UserConnect.select_follows_by_user_id(user.User_id)
    good_ratings_count,bad_ratings_count = Rating.select_rate_by_user_id(user.User_id)
    # ユーザーがいいねした商品
    items = Likes.likes_join_sell(Sell, user.User_id)
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'user/userdata.html', user=user, followed=followed, follows_count=len(follows),
        good_ratings_count=good_ratings_count, bad_ratings_count=bad_ratings_count,
        items=items, liked_list=liked_list
    )