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
    Sell, Buy
)
from flmapp.models.reaction import (
    BrowsingHistory, Likes
)
from flmapp.forms.sell import (
    SellUpdateFlgAndDeleteForm
)

bp = Blueprint('item', __name__, url_prefix='/item')


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def likes_count_processor():
    def likes_count(sell_id):
        """いいねの数をカウントして返す"""
        all_likes = Likes.select_likes_by_sell_id(sell_id)
        return len(all_likes)
    return dict(likes_count=likes_count)


@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
def itemdata(item_id):
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    item = Sell.query.get(item_id)
    buy_user = ""
    buy = Buy.select_buy_by_sell_id(item_id)
    if buy:
        buy_user = buy.User_id
    if item is None:
        return redirect(url_for('route.home'))
    form = SellUpdateFlgAndDeleteForm(request.form)
    # ログイン中のユーザーが過去にどの商品をいいねしたかを格納しておく
    liked_list = []
    liked = Likes.liked_exists(item_id)
    if liked:
        liked_list.append(item_id)
    # 閲覧履歴登録処理
    browsinghistory = BrowsingHistory(
        Sell_id = item_id,
        User_id = current_user.User_id
    )
    with db.session.begin(subtransactions=True):
        BrowsingHistory.create_new_browsinghistory(browsinghistory)
    db.session.commit()
    return render_template('item/itemdata.html', item=item, form=form, liked_list=liked_list, buy_user=buy_user)