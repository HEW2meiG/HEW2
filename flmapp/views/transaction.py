import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User, ShippingAddress
)
from flmapp.models.trade import (
    Sell, Buy
)

bp = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp.route('/<int:item_id>', methods=['GET', 'POST'])
def transaction(item_id):
    item = Sell.select_sell_by_sell_id(item_id)
    buy = Buy.select_buy_by_sell_id(item_id)
    shippingaddress = ShippingAddress.search_shippingaddress(buy.ShippingAddress_id)
    return render_template('transaction/transaction.html', item=item, buy=buy, shippingaddress=shippingaddress)