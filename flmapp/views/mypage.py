from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.auth import (
    User, UserInfo, Address, PasswordResetToken
)
from flmapp.forms.mypage import (
   ProfileForm, ChangePasswordForm
)

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required # login_requiredを追加するとログインしていないとアクセスができないようになる
def mypagetop():
    return render_template('mypage/mypage.html')

# プロフィール設定ページ
@bp.route('/profile', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def user():
    form = ProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        # current_user:セッションに保存してあるuser_idから、userを取得
        # ログイン中のユーザーのid
        user_id = current_user.get_id()
        # ユーザーIDによってユーザーを取得
        user = User.select_user_by_id(user_id)
        # データベース処理
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.prof_comment = form.prof_comment.data
            # ファイルアップロード処理
            #! ファイルアップロード方法を変える----------------------
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = str(user.User_id) + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flmapp/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
            #! -------------------------------------------------
        db.session.commit()
        flash('ユーザ情報の更新に成功しました')
    return render_template('mypage/profile.html', form=form)

# パスワード・メール変更ページ
@bp.route('/change_password', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        # ログイン中のユーザーIDによってユーザーを取得
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        # データベース処理
        with db.session.begin(subtransactions=True):
            # email更新
            user.email = form.email.data
            if password:
                # パスワード更新処理(パスワードのハッシュ化とユーザーの有効化)
                user.save_new_password(password)
        db.session.commit()
        flash('更新に成功しました')
        return redirect(url_for('auth.login'))
    return render_template('mypage/change_password.html', form=form)