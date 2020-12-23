import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell
)

bp = Blueprint('item', __name__, url_prefix='/item')

#! 出品したユーザーとログイン中のユーザーが一緒なら購入ボタンを消す

@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
def itemdata(item_id):
    item = Sell.query.get(item_id)
    return render_template('item/itemdata.html', item=item)