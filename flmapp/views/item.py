import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, session
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
from flmapp.models.reaction import (
    BrowsingHistory
)
from flmapp.forms.sell import (
    SellUpdateFlgAndDeleteForm
)

bp = Blueprint('item', __name__, url_prefix='/item')


@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
def itemdata(item_id):
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    item = Sell.query.get(item_id)
    if item is None:
        return redirect(url_for('route.home'))
    form = SellUpdateFlgAndDeleteForm(request.form)
    # 閲覧履歴登録処理
    browsinghistory = BrowsingHistory(
        Sell_id = item_id,
        User_id = current_user.User_id
    )
    with db.session.begin(subtransactions=True):
        BrowsingHistory.create_new_browsinghistory(browsinghistory)
    db.session.commit()
    return render_template('item/itemdata.html', item=item, form=form)