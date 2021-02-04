from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify, session
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db

import random # レコメンド
from flmapp.utils.recommendations import (
    getRecommendations, topMatches
)# レコメンド
from flmapp.models.user import (
    User
)
from flmapp.models.reaction import (
    Likes, UserConnect, BrowsingHistory
)
from flmapp.models.trade import (
    Sell, Buy
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


def recommend():
    """協調フィルタリングユーザーベースレコメンド"""
    # データ整形
    prefs={}
    users = User.query.all()
    items = Sell.query.all()
    on_display = Sell.select_all_sell_by_deal_status(1)
    followed = UserConnect.select_follows_user_id_by_user_id(current_user.User_id)
    # 一次元タプルに変換
    on_display = sum(on_display, ())
    followed = sum(followed, ())
    for user in users:
        userid = user.User_id
        prefs.setdefault(userid,{})
        for item in items:
            itemid = item.Sell_id
            rating = 0
            bought = Buy.buy_exists_user_id(userid, itemid)
            if bought:
                rating += 3
            else:
                b_history = BrowsingHistory.b_history_exists(userid, itemid)
                if b_history:
                    rating += 1
                liked = Likes.liked_exists_user_id(userid, itemid)
                if liked:
                    rating += 2
            prefs[userid][itemid] = rating
    # 商品レコメンド
    recommends = getRecommendations(prefs,current_user.User_id,on_display)
    # ユーザーレコメンド
    u_recommends = topMatches(prefs,current_user.User_id, followed)
    print(u_recommends)
    r_item_list = []
    if recommends is not None:
        for recommend in recommends:
            recommend_id = int(recommend)
            r_item_list.append(Sell.select_sell_by_sell_id(recommend_id))
    elif recommends is None:
        r_item_list = []
    r_user_list = []
    if u_recommends is not None:
        for u_recommend in u_recommends:
            u_recommend_id = int(u_recommend)
            r_user_list.append(User.select_user_by_id(u_recommend_id))
    elif u_recommends is None:
        r_user_list = []
    return r_item_list,r_user_list


@bp.route('/')
def home():
    """ホーム(新着順)"""
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    # 出品状態、有効フラグが有効の商品を新着順に取り出す
    items = Sell.select_new_sell()
    # レコメンドリスト
    r_item_list = []
    r_user_list = []
    if current_user.is_authenticated:
        r_item_list,r_user_list = recommend()
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'home.html',
        items=items,
        liked_list=liked_list,
        r_item_list=r_item_list,
        r_user_list=r_user_list
    )

@bp.route('/timeline')
@login_required
def timeline():
    """ホーム(タイムライン)"""
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    items = UserConnect.select_timeline_sell(Sell)
    # レコメンドリスト
    r_item_list = []
    r_user_list = []
    r_item_list,r_user_list = recommend()
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'home.html',
        items=items,
        liked_list=liked_list,
        r_item_list=r_item_list,
        r_user_list=r_user_list
    )


@bp.route('/hit')
def hit():
    """ホーム(ヒット)"""
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    items = BrowsingHistory.select_hit_sell(Sell)
    # レコメンドリスト
    r_item_list = []
    r_user_list = []
    if current_user.is_authenticated:
        r_item_list,r_user_list = recommend()
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    for item in items:
        liked = Likes.liked_exists(item.Sell_id)
        if liked:
            liked_list.append(item.Sell_id)
    return render_template(
        'home.html',
        items=items,
        liked_list=liked_list,
        r_item_list=r_item_list,
        r_user_list=r_user_list
    )


@bp.app_errorhandler(404)
def page_not_found(e):
    """ページが見つからない場合"""
    return redirect(url_for('route.home')), 404


@bp.app_errorhandler(405)
def method_not_allowed(e):
    """許可されていないHTTPメソッドアクセス時エラー"""
    return render_template('405.html'), 405


@bp.app_errorhandler(500)
def server_error(e):
    """サーバーエラー"""
    return render_template('500.html'), 500