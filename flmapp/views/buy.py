import os
import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, session
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db
from functools import wraps # カスタムデコレーターに使用

from flmapp.models.user import (
    User, ShippingAddress, Credit
)
from flmapp.models.trade import (
    Sell, Buy, Deal_status
)
from flmapp.forms.buy import (
   HiddenBuyForm, PayWayForm, ShippingAddressForm,
   ShippingAddressRegisterForm, HiddenShippingAddressDeleteForm,
   ShippingAddressEditForm, CreditRegisterForm,
   HiddenPayWayDeleteForm
)

bp = Blueprint('buy', __name__, url_prefix='/buy')

def check_buy(func):
    """
        出品したユーザーとログイン中のユーザーが一致した場合,
        取引状態、出品状態、有効フラグが無効だった場合,
        リダイレクト
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        sell_id = kwargs['item_id']
        sell = Sell.select_sell_by_sell_id(sell_id)
        user_id = current_user.get_id()
        if sell.user.User_id == user_id:
            flash("出品者の商品は購入できません。")
            return redirect(url_for('item.itemdata', item_id=sell_id))
        elif not sell.sell_flg:
            flash("選択された商品は購入できません。")
            return redirect(url_for('route.home'))
        elif not sell.is_active:
            flash("選択された商品は購入できません。")
            return redirect(url_for('route.home'))
        elif sell.deal_status != Deal_status['出品中']:
            flash("選択された商品は出品中ではありません。")
            return redirect(url_for('item.itemdata', item_id=sell_id))
        return func(*args, **kwargs)
    return decorated_function


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def shippingaddresses_processor():
    def search_shippingaddress(ShippingAddress_id):
        """配送先住所レコードを返す"""
        shippingaddress = ShippingAddress.search_shippingaddress(ShippingAddress_id)
        return shippingaddress
    return dict(search_shippingaddress=search_shippingaddress)


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def credit_processor():
    def search_credit(Credit_id):
        """クレジット情報レコードを返す"""
        credit = Credit.search_credit(Credit_id)
        return credit
    return dict(search_credit=search_credit)


# カスタムテンプレートフィルター
@bp.app_template_filter('credit_num_format')
def credit_num_format(value):
    """クレジットカード番号下4ケタ表示フィルター"""
    return '*'*12 + str(value)[-4:]


@bp.route('/<int:item_id>', methods=['GET', 'POST'])
@login_required
@check_buy
def buy(item_id):
    """購入処理"""
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
        # セッションの破棄
        session.pop('pay_way', None)
        session.pop('Credit_id', None)
        session.pop('ShippingAddress_id', None)
        return render_template('buy/buy_complete.html', item=item, buy=buy)
    return render_template('buy/buy.html', item=item, form=form)


@bp.route('/<int:item_id>/pay_way', methods=['GET', 'POST'])
@login_required
@check_buy
def pay_way(item_id):
    """支払い方法選択処理"""
    if 'pay_way' in session and session['pay_way'] == 1:
        default_pay_way = 0
    elif 'pay_way' in session and session['pay_way'] == 2:
        default_pay_way = session['Credit_id']
    elif current_user.default_pay_way == 1:
        default_pay_way = 0
    elif current_user.default_pay_way == 2:
        default_pay_way = current_user.default_Credit_id
    form = PayWayForm(request.form, pay_way=default_pay_way)
    delete_form = HiddenPayWayDeleteForm(request.form)
    credits = Credit.select_credits_by_user_id()
    if credits:
        form.pay_way.choices += [(credit.Credit_id, 'クレジットカード') for credit in credits]
    if request.method=='POST' and form.validate():
        # 支払い方法をデフォルトに設定する場合
        if form.is_default.data:
            # 代金引き換えのvalue:0に設定済み(1だとCredit_idと重複し判断できないため)
            if form.pay_way.data == 0:
                # デフォルト設定を代金引き換えに更新
                with db.session.begin(subtransactions=True):
                    current_user.default_pay_way = 1
                    # デフォルト設定ですでにdefault_Credit_idが設定されていればNull値に更新
                    if current_user.default_Credit_id:
                        current_user.default_Credit_id = None
                db.session.commit()
            else:
                # デフォルト設定をクレジットに更新
                with db.session.begin(subtransactions=True):
                    current_user.default_pay_way = 2
                    current_user.default_Credit_id = int(form.pay_way.data)
                db.session.commit()
        if form.pay_way.data == 0:
            session['pay_way'] = 1
            session.pop('Credit_id', None)
        else:
            session['pay_way'] = 2
            session['Credit_id'] = int(form.pay_way.data)
        flash('支払い方法を選択しました。')
        return redirect(url_for('buy.buy', item_id=item_id))
    return render_template('buy/pay_way.html', item_id=item_id, form=form, credits=credits, delete_form=delete_form)


@bp.route('/<int:item_id>/pay_way_delete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_buy
def pay_way_delete(item_id):
    """支払い方法削除処理"""
    form = HiddenPayWayDeleteForm(request.form)
    if request.method == 'POST':
        with db.session.begin(subtransactions=True):
            # デフォルトで設定されているdefault_Credit_idが
            # 削除するdefault_Credit_idと一致していればNull値に更新し
            # default_pay_wayを1(代金引換)に更新する
            if current_user.default_Credit_id == int(form.Credit_id.data):
                current_user.default_pay_way = 1
                current_user.default_Credit_id = None
            Credit.delete_credit(int(form.Credit_id.data))
        db.session.commit()
        if 'Credit_id' in session and session['Credit_id'] == int(form.Credit_id.data):
            session.pop('Credit_id', None)
            session['pay_way'] = 1
        flash('削除しました')
    return redirect(url_for('buy.pay_way', item_id=item_id))


@bp.route('/<int:item_id>/credit_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_buy
def credit_register(item_id):
    """クレジットカード登録"""
    form = CreditRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        credit = Credit(
            # ユーザーID
            User_id = user_id,
            # クレジット名義人
            credit_name = form.credit_name.data,
            # クレジットカード番号
            credit_num = form.credit_num.data,
            # クレジット有効期限 Date型のため、日付はすべて1に設定するとする。
            expire = datetime.date(form.expiration_date02.data, form.expiration_date01.data, 1)
        )
        credit.security_code = str(form.security_code.data)
        # データベース処理
        with db.session.begin(subtransactions=True):
            credit.create_new_credit()
        db.session.commit()
        # デフォルトに設定する場合
        if form.is_default.data:
            with db.session.begin(subtransactions=True):
                current_user.default_pay_way = 2
                current_user.default_Credit_id = credit.Credit_id
            db.session.commit()
        session['pay_way'] = 2
        session['Credit_id'] = credit.Credit_id
        flash('登録しました')
        return redirect(url_for('buy.pay_way', item_id=item_id))
    return render_template('buy/credit_register.html', item_id=item_id, form=form)


@bp.route('/<int:item_id>/shippingaddress', methods=['GET', 'POST'])
@login_required
@check_buy
def shippingaddress(item_id):
    """配送先住所選択処理"""
    if 'ShippingAddress_id' in session:
        default_ShippingAddress_id = session['ShippingAddress_id']
    else:
        default_ShippingAddress_id = current_user.default_ShippingAddress_id
    form = ShippingAddressForm(request.form, ShippingAddress_id=default_ShippingAddress_id)
    delete_form = HiddenShippingAddressDeleteForm(request.form)
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
    return render_template('buy/shippingaddress.html', item_id=item_id, form=form, delete_form=delete_form, shippingaddresses=shippingaddresses)


@bp.route('/<int:item_id>/shippingaddress_register', methods=['GET', 'POST'])
@login_required
@check_buy
def shippingaddress_register(item_id):
    """配送先住所登録処理"""
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
        return redirect(url_for('buy.shippingaddress', item_id=item_id))
    return render_template('buy/shippingaddress_register.html', item_id=item_id, form=form)


@bp.route('/<int:item_id>/shippingaddress_delete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_buy
def shippingaddress_delete(item_id):
    """配送先住所削除処理"""
    form = HiddenShippingAddressDeleteForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            if current_user.default_ShippingAddress_id == int(form.ShippingAddress_id.data):
                current_user.default_ShippingAddress_id = None
            ShippingAddress.delete_shippingaddress(int(form.ShippingAddress_id.data))
        db.session.commit()
        if 'ShippingAddress_id' in session and session['ShippingAddress_id'] == int(form.ShippingAddress_id.data):
            session.pop('ShippingAddress_id', None)
        flash('削除しました')
    return redirect(url_for('buy.shippingaddress', item_id=item_id))


@bp.route('/<int:item_id>/shippingaddress_edit/<int:shippingaddress_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_buy
def shippingaddress_edit(item_id,shippingaddress_id):
    """配送先住所編集処理"""
    shippingaddress = ShippingAddress.search_shippingaddress(shippingaddress_id)
    form = ShippingAddressEditForm(request.form, pref01 = shippingaddress.prefecture)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            shippingaddress.last_name = form.last_name.data 
            shippingaddress.first_name = form.first_name.data 
            shippingaddress.last_name_kana = form.last_name_kana.data 
            shippingaddress.first_name_kana = form.first_name_kana.data 
            shippingaddress.zip_code = form.zip01.data 
            shippingaddress.prefecture = form.pref01.data
            shippingaddress.address1 = form.addr01.data 
            shippingaddress.address2 = form.addr02.data
            shippingaddress.address3 = form.addr03.data 
        db.session.commit()
        flash('更新しました')
        return redirect(url_for('buy.shippingaddress', item_id=item_id))
    return render_template('buy/shippingaddress_edit.html', item_id=item_id, form=form, shippingaddress=shippingaddress)