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
    Sell
)
from flmapp.forms.buy import (
   BuyForm
)

bp = Blueprint('buy', __name__, url_prefix='/buy')

#! デコレーター追加する(取引画面User制限)

@bp.route('/<int:item_id>', methods=['GET', 'POST'])
def buy(item_id):
    form = BuyForm(request.form)
    #! 配送先住所複数登録可能にする
    shippingaddresses = ShippingAddress.select_shippingaddress_by_user_id()
    credits = Credit.select_credit_by_user_id()
    if credits:
        form.pay_way.choices += [(credit.id, credit.credit_name) for credit in credits]
    
    item = Sell.query.get(item_id)
    return render_template('buy/buy.html', item=item, form=form)