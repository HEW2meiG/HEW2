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
from flmapp.models.message import (
    DealMessage
)
from flmapp.forms.transaction import (
    DealMessageForm
)


bp = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp.route('/<int:item_id>', methods=['GET', 'POST'])
def transaction(item_id):
    item = Sell.select_sell_by_sell_id(item_id)
    buy = Buy.select_buy_by_sell_id(item_id)
    shippingaddress = ShippingAddress.search_shippingaddress(buy.ShippingAddress_id)
    messageform = DealMessageForm(request.form)
    messages = DealMessage.get_messages_by_sell_id(item_id)
    # ログイン中のユーザーが出品者だった場合
    if current_user.User_id == item.User_id:
        dest_user = User.select_user_by_id(buy.User_id)
    # ログイン中のユーザーが購入者だった場合
    elif current_user.User_id == buy.User_id:
        dest_user = User.select_user_by_id(item.User_id)
    if request.method == 'POST' and messageform.validate():
        dealmessage = DealMessage(
            Sell_id = item_id,
            to_user_id = dest_user.User_id,
            from_user_id = current_user.User_id,
            message = messageform.message.data
        )
        # データベース登録処理
        with db.session.begin(subtransactions=True):
            dealmessage.create_new_dealmessage()
        db.session.commit()
        return redirect(url_for('transaction.transaction', item_id=item_id))
    return render_template(
        'transaction/transaction.html',
        item=item,
        buy=buy,
        shippingaddress=shippingaddress,
        messageform=messageform,
        messages=messages,
        dest_user=dest_user
    )