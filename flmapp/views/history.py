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
    Sell
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
    items = Sell.select_sell_by_deal_status(user_id, 1)
    return render_template('history/sell_history.html', items=items)


@bp.route('/sell_in_progress', methods=['GET', 'POST'])
@login_required
def sell_in_progress():
    """出品取引中履歴"""
    user_id = current_user.get_id()
    items = Sell.select_sell_by_deal_status(user_id, 2)
    return render_template('history/sell_history.html', items=items)


@bp.route('/sell_completed', methods=['GET', 'POST'])
@login_required
def sell_completed():
    """出品取引済み履歴"""
    user_id = current_user.get_id()
    items = Sell.select_sell_by_deal_status(user_id, 3)
    return render_template('history/sell_history.html', items=items)


@bp.route('/buy_in_progress', methods=['GET', 'POST'])
@login_required
def buy_in_progress():
    """購入取引中履歴"""
    user_id = current_user.get_id()
    items = Sell.sell_join_buy_deal_status(user_id, 2)
    return render_template('history/buy_history.html', items=items)


@bp.route('/buy_completed', methods=['GET', 'POST'])
@login_required
def buy_completed():
    """購入取引済み履歴"""
    user_id = current_user.get_id()
    items = Sell.sell_join_buy_deal_status(user_id, 3)
    return render_template('history/buy_history.html', items=items)
