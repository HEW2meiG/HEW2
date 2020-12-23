from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_required, current_user
)
from flmapp import db

from flmapp.models.user import (
    User
)
from flmapp.models.reaction import (
    UserConnect
)


bp = Blueprint('user', __name__, url_prefix='/user')


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def followers_count_processor():
    def followers_count(user_id):
        """フォロワーの数をカウントして返す"""
        all_followers = UserConnect.select_followers_by_user_id(user_id)
        return len(all_followers)
    return dict(followers_count=followers_count)


#! あとからユーザーコードに変更します
@bp.route('/userdata/<int:user_id>', methods=['GET', 'POST'])
def userdata(user_id):
    user = User.select_user_by_id(user_id) #! あとからユーザーコードで検索をかけるよう変更
    # ログイン中のユーザーがユーザーページのユーザーをフォローしているかの判定
    followed = UserConnect.followed_exists(user_id)
    return render_template('user/userdata.html', user=user, followed=followed)