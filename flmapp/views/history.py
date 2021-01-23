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


# 出品した本
@bp.route('/sell_history', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_history():
    user_id = current_user.get_id()
    # 出品中の本
    items = Sell.select_sell_by_deal_status(user_id, 1)
    return render_template('history/sell_history.html', items=items)