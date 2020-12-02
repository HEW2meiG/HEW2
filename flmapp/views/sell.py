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
from flmapp.forms.sell import (
    SellForm, HiddenSellForm
)

bp = Blueprint('sell', __name__, url_prefix='/sell')

@bp.route('/', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell():
    form = SellForm(request.form)
    if request.method=='POST' and form.validate():
        if form.submit(value='出品画面に戻る'):
            return render_template('sell/sell.html', form=form)
    return render_template('sell/sell.html', form=form)

@bp.route('/preview', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_preview():
    form = SellForm(request.form)
    hiddenform = HiddenSellForm()
    if request.method=='POST' and form.validate():
        return render_template('sell/sell_preview.html', form=form, hiddenform=hiddenform)
    return redirect(url_for('route.home'))

@bp.route('/sell_complete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_register():
    form = SellForm(request.form)
    if request.method=='POST' and form.validate():
        userid = current_user.get_id()
        sell = Sell(
            User_id = userid,
            sell_title = form.sell_title.data,
            key1 = form.key1.data,
            key2 = form.key2.data,
            key3 = form.key3.data,
            sell_comment = form.sell_comment.data,
            price = form.price.data,
            genre = form.genre.data,
            item_state = form.item_state.data,
            postage = form.postage.data,
            send_way = form.send_way.data,
            consignor = form.consignor.data,
            schedule = form.schedule.data,
            remarks = form.remarks.data
        )
        # データベース処理
        with db.session.begin(subtransactions=True):
            # Sellテーブルにレコードの挿入
            sell.create_new_sell()
        db.session.commit()
        return render_template('sell/sell_complete.html')
    return redirect(url_for('route.home'))