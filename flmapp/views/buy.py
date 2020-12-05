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
    User, ShippingAddress, Credit
)
from flmapp.models.trade import (
    Sell, Buy, Deal_status
)
from flmapp.forms.buy import (
   HiddenBuyForm, PayWayForm, ShippingAddressForm,
   ShippingAddressRegisterForm
)

bp = Blueprint('buy', __name__, url_prefix='/buy')

#! デコレーター追加する(取引画面User制限)
#! 出品したユーザーとログイン中のユーザーが一緒なら購入できないようにする

@bp.route('/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def buy(item_id):
    form = HiddenBuyForm(request.form)
    item = Sell.select_sell_by_sell_id(item_id)
    if request.method=='POST' and form.validate():
        user_id = current_user.get_id()
        buy = Buy(
            User_id = user_id,
            Sell_id = item_id,
            pay_way = form.pay_way.data,
            Credit_id = form.Credit_id.data,
            ShippingAddress_id = form.ShippingAddress_id.data
        )
        with db.session.begin(subtransactions=True):
            buy.create_new_buy()
            item.deal_status = Deal_status['取引中']
        db.session.commit()
        return render_template('buy/buy_complete.html', item=item, buy=buy)
    return render_template('buy/buy.html', item=item, form=form)

@bp.route('/<int:item_id>/pay_way', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def pay_way(item_id):
    form = PayWayForm(request.form)
    credits = Credit.select_credits_by_user_id()
    if credits:
        form.pay_way.choices += [(credit.Credit_id, 'クレジットカード') for credit in credits]
    if request.method=='POST' and form.validate():
        if form.pay_way.data == 1:
            session['pay_way'] = 1
        else:
            session['pay_way'] = 2
            session['Credit_id'] = form.pay_way.data
        return redirect(url_for('buy.buy', item_id=item_id))
    return render_template('buy/pay_way.html', item_id=item_id, form=form)

@bp.route('/<int:item_id>/shippingaddress', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress(item_id):
    if session['ShippingAddress_id']:
        default_ShippingAddress_id = session['ShippingAddress_id']
    else:
        default_ShippingAddress_id = current_user.default_ShippingAddress_id
    form = ShippingAddressForm(request.form, ShippingAddress_id=default_ShippingAddress_id)
    shippingaddresses = ShippingAddress.select_shippingaddresses_by_user_id()
    if shippingaddresses:
        form.ShippingAddress_id.choices += [(int(shippingaddress.ShippingAddress_id),'この住所に送る') for shippingaddress in shippingaddresses]
    if request.method=='POST' and form.validate():
        # 配送先をデフォルトに設定する場合
        if form.is_default.data:
            with db.session.begin(subtransactions=True):
                current_user.default_ShippingAddress_id = form.ShippingAddress_id.data
            db.session.commit()
        session['ShippingAddress_id'] = form.ShippingAddress_id.data
        return redirect(url_for('buy.buy', item_id=item_id))
    return render_template('buy/shippingaddress.html', item_id=item_id, form=form)

# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def shippingaddresses_processor():
    def search_shippingaddress(ShippingAddress_id):
        shippingaddress = ShippingAddress.search_shippingaddress(ShippingAddress_id)
        return shippingaddress
    return dict(search_shippingaddress=search_shippingaddress)

@bp.route('/<int:item_id>/shippingaddress_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress_register(item_id):
    form = ShippingAddressRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        shippingaddress = ShippingAddress(
            User_id = user_id,
            last_name = form.last_name.data,
            first_name = form.first_name.data,
            last_name_kana = form.last_name_kana.data,
            first_name_kana = form.first_name_kana.data,
            zip_code = form.zip01.data,
            prefecture = form.pref01.data,
            address1 = form.addr01.data,
            address2 = form.addr02.data,
            address3 = form.addr03.data
        )
        # データベース登録処理
        with db.session.begin(subtransactions=True):
            shippingaddress.create_new_shippingaddress()
        db.session.commit()
        # 配送先をデフォルトに設定する場合
        if form.is_default.data:
            with db.session.begin(subtransactions=True):
                current_user.default_ShippingAddress_id = shippingaddress.ShippingAddress_id
            db.session.commit()
        session['ShippingAddress_id'] = shippingaddress.ShippingAddress_id
        flash('登録しました')
        return redirect(url_for('buy.buy', item_id=item_id))
    return render_template('buy/shippingaddress_register.html', form=form)