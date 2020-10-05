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
   UserForm, ChangePasswordForm
)

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required # ログインしないと表示されないパス
def mypagetop():
    return render_template('mypage/mypage.html')

@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = str(user.User_id) + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flmapp/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        flash('ユーザ情報の更新に成功しました')
    return render_template('mypage/user.html', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_id(current_user.get_id())
        password = form.password.data
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
        db.session.commit()
        flash('パスワードの更新に成功しました')
        return redirect(url_for('auth.login'))
    return render_template('mypage/change_password.html', form=form)