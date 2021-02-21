from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify, session
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell, Buy
)
from flmapp.models.reaction import (
    Likes, UserConnect
)
from flmapp.models.message import(
    PostMessage, DealMessage
)

bp = Blueprint('history', __name__, url_prefix='/mypage/history')


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)


@bp.route('/sell_on_display', methods=['GET', 'POST'])
@login_required
def sell_on_display():
    """出品中履歴"""
    user_id = current_user.get_id()
    next_url_1 = prev_url_1 = items = None
    page = request.args.get('page', 1, type=int)
    posts = Sell.select_sell_by_deal_status_page(user_id, 1, page)
    next_url = url_for('history.sell_on_display', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('history.sell_on_display', page=posts.prev_num) if posts.has_prev else None
    items = posts.items
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url, liked_list=liked_list)


@bp.route('/sell_in_progress', methods=['GET', 'POST'])
@login_required
def sell_in_progress():
    """出品取引中履歴"""
    user_id = current_user.get_id()
    next_url_2 = prev_url_2 = items = None
    page = request.args.get('page', 1, type=int)
    posts = Sell.select_sell_by_deal_status_page(user_id, 2, page)
    next_url = url_for('history.sell_in_progress', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('history.sell_in_progress', page=posts.prev_num) if posts.has_prev else None
    items = posts.items
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url, liked_list=liked_list)


@bp.route('/sell_completed', methods=['GET', 'POST'])
@login_required
def sell_completed():
    """出品取引済み履歴"""
    user_id = current_user.get_id()
    next_url_3 = prev_url_3 = items = None
    page = request.args.get('page', 1, type=int)
    posts = Sell.select_sell_by_deal_status_page(user_id, 3, page)
    next_url = url_for('history.sell_completed', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('history.sell_completed', page=posts.prev_num) if posts.has_prev else None
    items = posts.items
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url, liked_list=liked_list)


@bp.route('/buy_in_progress', methods=['GET', 'POST'])
@login_required
def buy_in_progress():
    """購入取引中履歴"""
    user_id = current_user.get_id()
    next_url_4 = prev_url_4 = items = None
    page = request.args.get('page', 1, type=int)
    posts = Buy.buy_join_sell_deal_status_page(user_id, 2, page)
    next_url_4 = url_for('history.buy_in_progress', page=posts.next_num) if posts.has_next else None
    prev_url_4 = url_for('history.buy_in_progress', page=posts.prev_num) if posts.has_prev else None
    items = posts.items
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template('history/buy_history.html', items=items, next_url_4=next_url_4, prev_url_4=prev_url_4, liked_list=liked_list)


@bp.route('/buy_completed', methods=['GET', 'POST'])
@login_required
def buy_completed():
    """購入取引済み履歴"""
    user_id = current_user.get_id()
    next_url_5 = prev_url_5 = items = None
    page = request.args.get('page', 1, type=int)
    posts = Buy.buy_join_sell_deal_status_page(user_id, 3, page)
    next_url_5 = url_for('history.buy_in_progress', page=posts.next_num) if posts.has_next else None
    prev_url_5 = url_for('history.buy_in_progress', page=posts.prev_num) if posts.has_prev else None
    items = posts.items
    liked_list = []
    if current_user.is_authenticated:
        for item in items:
            liked = Likes.liked_exists(item.Sell_id)
            if liked:
                liked_list.append(item.Sell_id)
    return render_template('history/buy_history.html', items=items, next_url_5=next_url_5, prev_url_5=prev_url_5, liked_list=liked_list)
