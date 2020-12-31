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
    Sell, Genre, Item_state, Postage, Send_way, Schedule, Deal_status
)
from flmapp.forms.sell import (
    SellForm, HiddenSellForm, SellUpdateForm
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

# 商品更新
@bp.route('/sell_update/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_update(item_id):
    sell = Sell.select_sell_by_sell_id(item_id)
    form = SellUpdateForm(
        request.form,
        sell_comment = str(sell.sell_comment),
        genre = str(sell.genre.name),
        item_state = str(sell.item_state.name),
        postage = str(sell.postage.name),
        send_way = str(sell.send_way.name),
        consignor = str(sell.consignor),
        schedule = str(sell.schedule.name),
        remarks = str(sell.remarks)
        )
    if request.method == 'POST' and form.validate():
        # ログイン中のユーザーIDによってユーザーを取得
        user = User.select_user_by_id(current_user.get_id())
        # データベース処理
        with db.session.begin(subtransactions=True):
            sell.sell_title = str(form.sell_title.data)
            sell.key1 = str(form.key1.data)
            sell.key2 = str(form.key2.data)
            sell.key3 = str(form.key3.data)
            sell.sell_comment = str(form.sell_comment.data)
            sell.price = int(form.price.data)
            sell.genre = Genre[str(form.genre.data)]
            sell.item_state = Item_state[str(form.item_state.data)]
            sell.postage = Postage[str(form.postage.data)]
            sell.send_way = Send_way[str(form.send_way.data)]
            sell.consignor = str(form.consignor.data)
            sell.schedule = Schedule[str(form.schedule.data)]
            sell.remarks = str(form.remarks.data)
        db.session.commit()
        flash('更新に成功しました')
    return render_template('sell/sell_update.html', form=form, sell=sell)


# 商品一時停止
@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_update_sell_flg_delete(item_id):
    item = Sell.query.get(item_id)
    # ログイン中のユーザーIDによってユーザーを取得
    user_id = current_user.get_id()
    sell = Sell.select_sell_by_sell_id(item_id)
    # データベース処理
    if request.method == 'POST':
        with db.session.begin(subtransactions=True):
            if (request.form.get('submit')) == '一時停止':
                if sell.sell_flg:
                    sell.sell_flg = False
                    print('出品一時停止')
                    flash('一時停止に更新しました')
                else:
                    sell.sell_flg = True
                    print('出品中')
                    flash('出品中に更新しました')
            elif (request.form.get('submit')) == '商品削除':
                Sell.delete_sell(item_id)
                flash('削除に成功しました')
        db.session.commit()
        if (request.form.get('submit')) == '商品削除':
            return redirect(url_for('route.home'))
    return render_template('item/itemdata.html', item=item, user_id=user_id)