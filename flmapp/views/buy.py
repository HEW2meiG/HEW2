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
    User, ShippingAddress, Credit
)
from flmapp.models.trade import (
    Sell, Buy
)
from flmapp.forms.buy import (
   HiddenBuyForm, PayWayForm
)

bp = Blueprint('buy', __name__, url_prefix='/buy')

#! デコレーター追加する(取引画面User制限)

@bp.route('/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def buy(item_id):
    hiddenform = HiddenBuyForm(request.form)
    item = Sell.select_sell_by_sell_id()
    return render_template('buy/buy.html', item=item, hiddenform=hiddenform)

@bp.route('/<int:item_id>/pay_way', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def pay_way(item_id):
    form = PayWayForm(request.form)
    credits = Credit.select_credits_by_user_id()
    if credits:
        form.pay_way.choices += [(credit.Credit_id, credit.credit_name) for credit in credits]
    if request.method=='POST' and form.validate():
        return render_template('buy/buy.html', form=form, hiddenform=hiddenform)
    return render_template('buy/pay_way.html', item_id=item_id, form=form)

    # shippingaddresses = ShippingAddress.select_shippingaddresses_by_user_id()