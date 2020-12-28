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

@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
def itemdata(item_id):
    item = Sell.query.get(item_id)
    # ログイン中のユーザーIDによってユーザーを取得
    user = User.select_user_by_id(current_user.get_id())
    if user:    
        if user.User_id == item.User_id:
            return render_template('item/my_itemdata.html', item=item)
        else:
            return render_template('item/itemdata.html', item=item)
    else:
        return render_template('item/itemdata.html', item=item)
