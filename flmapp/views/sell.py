import shutil # ファイルの移動時使用
import os
import glob # 画像のリサイズ
from datetime import datetime
from PIL import Image
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,
    current_app as app #Blueprint環境下で、設定値(config)を取得
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy
from functools import wraps # カスタムデコレーターに使用

from flmapp.utils.image_square import (
    crop_max_square
)
from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell, Genre, Item_state, Postage, Send_way, Schedule, Deal_status
)
from flmapp.models.reaction import (
    Likes, BrowsingHistory
)
from flmapp.forms.sell import (
    SellForm, HiddenSellForm, SellUpdateForm, SellUpdateFlgAndDeleteForm
)

bp = Blueprint('sell', __name__, url_prefix='/sell')

# 画像アップロード処理用関数 ここから--------------------------------------
def allowed_image(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]
#ここまで------------------------------------------------------------------

def check_sell(func):
    """
        出品者以外のユーザーがURLへ遷移した際
        リダイレクトを行う
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        sell_id = kwargs['item_id']
        sell = Sell.select_sell_by_sell_id(sell_id)
        if sell is None:
            return redirect(url_for('route.home'))
        else:
            if sell.User_id != current_user.User_id:
                return redirect(url_for('route.home'))
        return func(*args, **kwargs)
    return decorated_function

@bp.route('/', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell():
    form = SellForm(request.form)
    return render_template('sell/sell.html', form=form)

@bp.route('/preview', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_preview():
    form = SellForm()
    hiddenform = HiddenSellForm()
    if request.method=='POST' and form.validate():
        # 画像アップロード処理 ここから--------------------------
        # 画像ファイルがあった場合
        if request.files:
            image = request.files[form.item_picture_path.name]
            # 画像アップロード処理用関数
            if allowed_image(image.filename):
                # ファイル名から拡張子を取り出す
                ext = image.filename.rsplit('.', 1)[1]
                # imagenameはユーザーID+現在の時間+.拡張子
                imagename = str(current_user.User_id) + '_' + \
                            str(int(datetime.now().timestamp())) + '.' + ext
                # ファイルの保存
                image.save(os.path.join(app.config["ORIGINAL_ITEM_IMAGE_UPLOADS"], imagename))
                im = Image.open(os.path.join(app.config["ORIGINAL_ITEM_IMAGE_UPLOADS"], imagename))
                # 最大サイズの正方形に切り出したあと、300に縮小
                im_thumb = crop_max_square(im).resize((300, 300), Image.LANCZOS)
                # ファイルの保存
                im_thumb.save(os.path.join(app.config["ITEM_TEMP_IMAGE_UPLOADS"], imagename))
            else:
                flash('画像のアップロードに失敗しました。')
                return render_template('sell/sell.html', form=form)
        # 画像アップロード処理 ここまで--------------------------
        return render_template('sell/sell_preview.html', form=form, hiddenform=hiddenform, imagename=imagename)
    return render_template('sell/sell.html', form=form)


@bp.route('/sell_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_register():
    form = SellForm(request.form)
    if request.method=='POST':
        # 画像ファイルの移動 item_temp_image->item_image
        shutil.move(os.path.join(app.config["ITEM_TEMP_IMAGE_UPLOADS"], form.item_picture_path.data), app.config["ITEM_IMAGE_UPLOADS"])
        userid = current_user.get_id()
        sell = Sell(
            User_id = userid,
            sell_title = form.sell_title.data,
            key1 = form.key1.data,
            key2 = form.key2.data,
            key3 = form.key3.data,
            sell_comment = form.sell_comment.data,
            price = form.price.data,
            item_picture_path = form.item_picture_path.data,
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
        return redirect(url_for('sell.sell_complete', item_id=sell.Sell_id))
    return redirect(url_for('route.home'))

@bp.route('/sell_complete/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_sell
def sell_complete(item_id):
    sell = Sell.select_sell_by_sell_id(item_id)
    return render_template('sell/sell_complete.html', item=sell)

# 商品更新
@bp.route('/sell_update/<int:item_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
@check_sell
def sell_update(item_id):
    sell = Sell.select_sell_by_sell_id(item_id)
    if sell.remarks==None:
        remarks = ''
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
        # 画像アップロード処理 ここから--------------------------
        imagename = ''
        image = request.files[form.item_picture_path.name]
        # 画像ファイルがあった場合
        if image:
            # 画像アップロード処理用関数
            if allowed_image(image.filename):
                # ファイル名から拡張子を取り出す
                ext = image.filename.rsplit('.', 1)[1]
                # imagenameはユーザーID+現在の時間+.拡張子
                imagename = str(current_user.User_id) + '_' + \
                            str(int(datetime.now().timestamp())) + '.' + ext
                # ファイルの保存
                image.save(os.path.join(app.config["ORIGINAL_ITEM_IMAGE_UPLOADS"], imagename))
                im = Image.open(os.path.join(app.config["ORIGINAL_ITEM_IMAGE_UPLOADS"], imagename))
                # 最大サイズの正方形に切り出したあと、300に縮小
                im_thumb = crop_max_square(im).resize((300, 300), Image.LANCZOS)
                # ファイルの保存
                im_thumb.save(os.path.join(app.config["ITEM_IMAGE_UPLOADS"], imagename))
            else:
                flash('画像のアップロードに失敗しました。')
                return render_template('sell/sell.html', form=form)
        # 画像アップロード処理 ここまで--------------------------
        # データベース処理
        with db.session.begin(subtransactions=True):
            if imagename: # imagenameが設定されていれば(画像があれば)更新する
                sell.item_picture_path = imagename
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
        return redirect(url_for('item.itemdata', item_id=item_id))
    return render_template('sell/sell_update.html', form=form, sell=sell)

# 商品一時停止
@bp.route('/sell_flg_update', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_flg_update():
    form = SellUpdateFlgAndDeleteForm(request.form)
    # データベース処理
    if request.method == 'POST':
        sell = Sell.select_sell_by_sell_id(form.Sell_id.data)
        with db.session.begin(subtransactions=True):
            if sell.sell_flg:
                sell.sell_flg = False
                flash('出品を一時停止しました')
            else:
                sell.sell_flg = True
                flash('出品を再開しました')
        db.session.commit()
        return redirect(url_for('item.itemdata', item_id=form.Sell_id.data))
    return redirect(url_for('route.home'))

# 商品削除
@bp.route('/sell_delete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def sell_delete():
    form = SellUpdateFlgAndDeleteForm(request.form)
    if request.method == 'POST':
        with db.session.begin(subtransactions=True):
            Sell.delete_sell(form.Sell_id.data)
            BrowsingHistory.delete_b_history(form.Sell_id.data)
            Likes.delete_all_like(form.Sell_id.data)
        db.session.commit()
        flash('削除しました')
        return redirect(url_for('history.sell_on_display'))
    return redirect(url_for('route.home'))
    
