import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User, ShippingAddress
)
from flmapp.models.trade import (
    Sell, Buy, Rating, Deal_status
)
from flmapp.models.message import (
    DealMessage
)
from flmapp.forms.transaction import (
    DealMessageForm, NoticeRatingForm
)
from flmapp.utils.message_format import make_deal_message_format, make_old_deal_message_format

bp = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp.route('/<int:item_id>', methods=['GET', 'POST'])
@login_required
def transaction(item_id):
    """取引画面処理"""
    item = Sell.select_sell_by_sell_id(item_id)
    buy = Buy.select_buy_by_sell_id(item_id)
    shippingaddress = ShippingAddress.search_shippingaddress(buy.ShippingAddress_id)
    messageform = DealMessageForm(request.form)
    messages = DealMessage.get_messages_by_sell_id(item_id)
    noticeform = NoticeRatingForm(request.form)
    # ログイン中のユーザーが出品者だった場合
    if current_user.User_id == item.User_id:
        dest_user = User.select_user_by_id(buy.User_id)
    # ログイン中のユーザーが購入者だった場合
    elif current_user.User_id == buy.User_id:
        dest_user = User.select_user_by_id(item.User_id)
    read_message_ids = [message.DealMessage_id for message in messages if (not message.is_read) and (message.from_user_id == int(dest_user.User_id))]
    if read_message_ids:
        with db.session.begin(subtransactions=True):
            # is_readをTrueに更新
            DealMessage.update_is_read_by_ids(read_message_ids)
        db.session.commit()
    not_checked_message_ids = [message.DealMessage_id for message in messages if message.is_read and (not message.is_checked) and (message.from_user_id == int(current_user.User_id))]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            DealMessage.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    if request.method == 'POST' and messageform.validate(read_message_ids):
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
        dest_user=dest_user,
        noticeform=noticeform
    )


@bp.route('/message_ajax', methods=['GET'])
@login_required
def message_ajax():
    dest_user_id = request.args.get('dest_user_id', -1, type=int)
    sell_id = request.args.get('sell_id', -1, type=int)
    dest_user = User.select_user_by_id(dest_user_id)
    not_read_messages = DealMessage.select_not_read_messages(dest_user_id, current_user.User_id, sell_id)
    not_checked_messages = DealMessage.select_not_checked_messages(current_user.User_id, dest_user_id, sell_id)
    not_read_message_ids = [not_read_message.DealMessage_id for not_read_message in not_read_messages]
    if not_read_message_ids:
        with db.session.begin(subtransactions=True):
            # is_readをTrueに更新
            DealMessage.update_is_read_by_ids(not_read_message_ids)
        db.session.commit()
    not_checked_message_ids = [not_checked_message.DealMessage_id for not_checked_message in not_checked_messages]
    if not_checked_message_ids:
        with db.session.begin(subtransactions=True):
            # is_checkedをTrueに更新
            DealMessage.update_is_checked_by_ids(not_checked_message_ids)
        db.session.commit()
    return jsonify(data=make_deal_message_format(dest_user, not_read_messages), checked_message_ids=not_checked_message_ids)


@bp.route('/load_old_messages', methods=['GET'])
@login_required
def load_old_messages():
    dest_user_id = request.args.get('dest_user_id', -1, type=int)
    sell_id = request.args.get('sell_id', -1, type=int)
    offset_value = request.args.get('offset_value', -1, type=int)
    if dest_user_id == -1 or offset_value == -1:
        return
    messages = DealMessage.get_messages_by_sell_id(sell_id, offset_value*50)
    dest_user = User.select_user_by_id(dest_user_id)
    return jsonify(data=make_old_deal_message_format(dest_user, messages))


@bp.route('/notice_rating/<int:item_id>', methods=['POST'])
@login_required
def notice_rating(item_id):
    sell = Sell.select_sell_by_sell_id(item_id)
    buy = Buy.select_buy_by_sell_id(item_id)
    form = NoticeRatingForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.notice_condition.data == 'has_sent':
            with db.session.begin(subtransactions=True):
                sell.has_sent = True
            db.session.commit()
            flash('発送通知を送信しました。')
            return redirect(url_for('transaction.transaction', item_id=item_id))
        if form.notice_condition.data == 'has_got':
            rating = Rating(
                Sell_id = item_id,
                to_user_id = sell.User_id,
                from_user_id = current_user.User_id,
                rating = form.rating.data,
                rating_message = form.rating_message.data
            )
            with db.session.begin(subtransactions=True):
                rating.create_new_rating()
                sell.has_got = True
            db.session.commit()
            flash('受け取り確認と評価を送信しました')
            return redirect(url_for('transaction.transaction', item_id=item_id))
        if form.notice_condition.data == 'seller_rating':
            rating = Rating(
                Sell_id = item_id,
                to_user_id = buy.User_id,
                from_user_id = current_user.User_id,
                rating = form.rating.data,
                rating_message = form.rating_message.data
            )
            with db.session.begin(subtransactions=True):
                rating.create_new_rating()
                sell.deal_status = Deal_status['取引済み']
            db.session.commit()
            flash('評価を送信しました。取引が完了しました。')
            return redirect(url_for('transaction.transaction', item_id=item_id))
    return redirect(url_for('transaction.transaction', item_id=item_id))