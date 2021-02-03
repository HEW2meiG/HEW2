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


@bp.route('/sell_on_display', methods=['GET', 'POST'])
@login_required
def sell_on_display():
    """出品中履歴"""
    user_id = current_user.get_id()
    next_url = prev_url = None
    page = request.args.get('page', 1, type=int)
    posts = Sell.select_sell_by_deal_status(user_id, 1, page)
    next_url = url_for('app.sell_in_progress', page=posts.next_num, user_id=user.id) if posts.has_next else None
    prev_url = url_for('app.sell_in_progress', page=posts.prev_num, user_id=user.id) if posts.has_prev else None
    items = posts.items
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url)


@bp.route('/sell_in_progress', methods=['GET', 'POST'])
@login_required
def sell_in_progress():
    """出品取引中履歴"""
    user_id = current_user.get_id()
    items = Sell.select_sell_by_deal_status(user_id, 2, 1)
    next_url = prev_url = None
    if items:
        page = request.args.get('page', 1, type=int)
        posts = Sell.select_sell_by_deal_status(user.id, 2, page)
        next_url = url_for('app.sell_in_progress', page=posts.next_num, user_id=user.id) if posts.has_next else None
        prev_url = url_for('app.sell_in_progress', page=posts.prev_num, user_id=user.id) if posts.has_prev else None
    items = posts.items
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url)


@bp.route('/sell_completed', methods=['GET', 'POST'])
@login_required
def sell_completed():
    """出品取引済み履歴"""
    user_id = current_user.get_id()
    items = Sell.select_sell_by_deal_status(user_id, 3, 1)
    next_url = prev_url = None
    if items:
        page = request.args.get('page', 1, type=int)
        posts = Sell.select_sell_by_deal_status(user.id, 3, page)
        next_url = url_for('app.sell_in_progress', page=posts.next_num, user_id=user.id) if posts.has_next else None
        prev_url = url_for('app.sell_in_progress', page=posts.prev_num, user_id=user.id) if posts.has_prev else None
    items = posts.items
    return render_template('history/sell_history.html', items=items, next_url=next_url, prev_url=prev_url)


@bp.route('/buy_in_progress', methods=['GET', 'POST'])
@login_required
def buy_in_progress():
    """購入取引中履歴"""
    user_id = current_user.get_id()
    items = Buy.buy_join_sell_deal_status(user_id, 2)
    if items == [None]:
        return render_template('history/buy_history_none.html', items=items)
    return render_template('history/buy_history.html', items=items)


@bp.route('/buy_completed', methods=['GET', 'POST'])
@login_required
def buy_completed():
    """購入取引済み履歴"""
    user_id = current_user.get_id()
    items = Buy.buy_join_sell_deal_status(user_id, 3)
    if items == [None]:
        return render_template('history/buy_history_none.html', items=items)
    return render_template('history/buy_history.html', items=items)
    
