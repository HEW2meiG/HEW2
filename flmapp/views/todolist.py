from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, jsonify, session
)
import datetime
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell, Buy, Rating
)

bp = Blueprint('todolist', __name__, url_prefix='/todolist')


@bp.app_context_processor
def todolist_count():
    """やることリストの数をカウントして返す"""
    count = 0
    user_id = current_user.get_id()
    items = Sell.select_sall_status(user_id)
    for item in items:
        # 出品者
        if item.User_id==user_id:
            buy_data = Buy.select_buy_by_sell_id(item.Sell_id)
            rating = Rating.select_count_sell_id_to_user_id(item.Sell_id, user_id)
            # 未発送
            if item.has_sent == item.has_got == False:
                count += 1
            # 発送済みで受け取り・評価待ち
            elif item.has_sent == True and item.has_got == False:
                count += 0
            # 受け取り済みで相手が相互評価して自分がしてない
            elif item.has_sent == item.has_got == True and rating == 1:
                count += 1
        #購入者 
        else:
            rating = Rating.select_count_sell_id_to_user_id(item.Sell_id, item.User_id)
            # 発送済みで商品を受取ってない
            if item.has_sent == True and item.has_got == False:
                count += 1
            # 発送待ち
            elif item.has_sent == item.has_got == False:
                count += 0
            # 評価待ち
            elif item.has_sent == item.has_got == True:
                count += 0
    return dict(todolist_count=count)


@bp.route('/todolist', methods=['GET', 'POST'])
@login_required
def todolist():
    """やることリスト"""
    user_id = current_user.get_id()
    now = datetime.datetime.now()
    items = Sell.select_sall_status(user_id)
    todolists =[]
    for item in items:
        elapsed = now - item.update_at
        todolist_data = {"item" : None, "status" : 0, "elapsed_time" : "", "partner_username" : "", "partner_user_code" : "", "partner_picture_path" : ""}
        # 出品者
        if item.User_id==user_id:
            buy_data = Buy.select_buy_by_sell_id(item.Sell_id)
            todolist_data["partner_username"] = User.select_user_by_id(buy_data.User_id).username
            todolist_data["partner_user_code"] = User.select_user_by_id(buy_data.User_id).user_code
            todolist_data["partner_picture_path"] = User.select_user_by_id(buy_data.User_id).picture_path
            rating = Rating.select_count_sell_id_to_user_id(item.Sell_id, user_id)
            # 未発送
            if item.has_sent == item.has_got == False:
                todolist_data["status"] = 1
            # 発送済みで受け取り・評価待ち
            elif item.has_sent == True and item.has_got == False:
                todolist_data["status"] = 4
            # 受け取り済みで相手が相互評価して自分がしてない
            elif item.has_sent == item.has_got == True and rating == 1:
                todolist_data["status"] = 2
                rating_datas=Rating.select_sell_id_to_user_id(item.Sell_id, user_id)
                for rating_data in rating_datas:
                    print(rating_data.update_at)
                    elapsed = now - rating_data.update_at
                    print(elapsed.days/7)
        #購入者 
        else:
            todolist_data["partner_username"] = User.select_user_by_id(item.User_id).username
            todolist_data["partner_user_code"] = User.select_user_by_id(item.User_id).user_code
            todolist_data["partner_picture_path"] = User.select_user_by_id(item.User_id).picture_path
            rating = Rating.select_count_sell_id_to_user_id(item.Sell_id, item.User_id)
            # 発送済みで商品を受取ってない
            if item.has_sent == True and item.has_got == False:
                todolist_data["status"] = 3
            # 発送待ち
            elif item.has_sent == item.has_got == False:
                todolist_data["status"] = 4
            # 評価待ち
            elif item.has_sent == item.has_got == True:
                todolist_data["status"] = 4
        print("*"*100)
        print(elapsed.days/7)
        # 経過時間
        if not elapsed.days//365 == 0:
            elapsed_time = str(elapsed.days//365) + "年"
        elif not elapsed.days//30 == 0:
            elapsed_time = str(elapsed.days//30) + "ヶ月"
        elif not elapsed.days//7 == 0:
            elapsed_time = str(elapsed.days//7) + "週間"
        elif not elapsed.days == 0:
            elapsed_time = str(elapsed.days) + "日"
        elif not elapsed.seconds//3600 == 0:
            elapsed_time = str(elapsed.seconds//3600) + "時間"
        elif not elapsed.seconds//60 == 0:
            elapsed_time = str(elapsed.seconds//60) + "分"
        else:
            elapsed_time = str(elapsed.seconds) + "秒"
        print(elapsed.seconds//60)
        print("*"*100)
        todolist_data["item"] = item
        todolist_data["elapsed_time"] = elapsed_time
        todolists.append(todolist_data)
        
    return render_template('todolist/todolist.html', todolists=todolists)