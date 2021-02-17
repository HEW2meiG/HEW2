from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_required, current_user
)
from flmapp import db

from flmapp.utils.recommendations import(
    associationRules
)
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


def u_recommend(userid,c_userid=None):
    """アソシエーション・ルール・マイニングによるレコメンド"""
    # データ整形
    transactions = []
    if c_userid is not None:
        followed = UserConnect.select_follows_user_id_by_user_id(c_userid)
        followed = sum(followed, ())
    users = User.query.all()
    for user in users:
        u_id = user.User_id
        follow_id = UserConnect.select_follows_user_id_by_user_id(u_id)
        follow_id = sum(follow_id, ())
        transactions.append(follow_id)
    print(transactions)
    if c_userid is not None:
        u_recommends = associationRules(transactions,userid,followed,c_userid)
    else:
        u_recommends = associationRules(transactions,userid)
    r_user_list = []
    if u_recommends:
        for u_recommend in u_recommends:
            u_recommend_id = int(u_recommend)
            r_user_list.append(User.select_user_by_id(u_recommend_id))
    elif not u_recommends:
        r_user_list = []
    return r_user_list


@bp.route('/userdata/<string:user_code>', methods=['GET', 'POST'])
def userdata(user_code):
    user = User.select_user_by_user_code(user_code)
    if user is None:
        return redirect(url_for('route.home'))
    follows = UserConnect.select_follows_by_user_id(user.User_id)
    good_ratings_count,bad_ratings_count = Rating.select_rate_by_user_id(user.User_id)
    # ユーザーが出品した商品
    items = Sell.select_sell_by_user_id_sort(user.User_id)
    # レコメンドリスト
    if current_user.is_authenticated:
        r_user_list = u_recommend(user.User_id,current_user.User_id)
    else:
        r_user_list = u_recommend(user.User_id)
    # ログイン中のユーザーがユーザーをフォローしているかの判定
    f_users = []
    f_users.append(user)
    f_users.extend(r_user_list)
    followed_list = []
    if current_user.is_authenticated:
        for f_user in f_users:
            followed = UserConnect.followed_exists(f_user.User_id)
            if followed:
                followed_list.append(f_user.User_id)
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template(
        'user/userdata.html', user=user, followed_list=followed_list, follows_count=len(follows),
        good_ratings_count=good_ratings_count, bad_ratings_count=bad_ratings_count,
        items=items, liked_list=liked_list, post_c=len(items), r_user_list=r_user_list
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
    # ユーザーが出品した商品
    sell_items = Sell.select_sell_by_user_id(user.User_id)
    # レコメンドリスト
    if current_user.is_authenticated:
        r_user_list = u_recommend(user.User_id,current_user.User_id)
    else:
        r_user_list = u_recommend(user.User_id)
    # ユーザーがいいねした商品
    items = Likes.likes_join_sell(Sell, user.User_id)
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template(
        'user/userdata.html', user=user, followed=followed, follows_count=len(follows),
        good_ratings_count=good_ratings_count, bad_ratings_count=bad_ratings_count,
        items=items, liked_list=liked_list, post_c=len(sell_items), r_user_list=r_user_list
    )