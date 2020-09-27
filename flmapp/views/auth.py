from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.auth import (
    User, UserInfo, Address, PasswordResetToken
)
from flmapp.forms.auth import (
    LoginForm, RegisterForm, CreateUserForm, ResetPasswordForm,
    ForgotPasswordForm, UserForm, ChangePasswordForm
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/logout')
def logout():
    logout_user() # ログアウト
    return redirect(url_for('auth.home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
        if user and user.is_active and user.validate_password(form.password.data):
            # ユーザーをログインさせる remember:セッションの期限が切れた後にユーザーを記憶する
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('auth.home')
            return redirect(next)
        elif not user:
            flash('存在しないユーザです')
        elif not user.is_active:
            flash('無効なユーザです。パスワードを再設定してください')
        elif not user.validate_password(form.password.data):
            flash('メールアドレスとパスワードの組み合わせが誤っています')
    return render_template('auth/login.html', form=form)

@bp.route('/mailregister', methods=['GET', 'POST'])
def register():
    form = CreateUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email = form.email.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ''
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        # メールに飛ばす
        print(
            f'パスワード設定用URL: http://127.0.0.1:5000/auth/userregister/{token}'
        )
        flash('本登録用のURLをお送りしました。ご確認ください')
        return redirect(url_for('auth.login'))
    return render_template('auth/create_user.html', form=form)

@bp.route('/userregister/<uuid:token>', methods=['GET', 'POST'])
def userregister(token):
    form = RegisterForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method=='POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        userinfo = UserInfo(
            User_id = user.User_id,
            last_name = form.last_name.data,
            first_name = form.first_name.data,
            last_name_kana = form.last_name_kana.data,
            first_name_kana = form.first_name_kana.data,
            birth = form.birth.data
        )
        address = Address(
            User_id = user.User_id,
            zip_code = form.zip01.data,
            prefecture = form.pref01.data,
            address1 = form.addr01.data,
            address2 = form.addr02.data,
            address3 = form.addr03.data
        )
        with db.session.begin(subtransactions=True):
            PasswordResetToken.delete_token(token)
            user.save_new_password(password)
            user.username = form.username.data
            userinfo.create_new_userinfo()
            address.create_new_useraddress()
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = str(user.User_id) + '_' + \
                    str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flmapp/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        flash('新規会員登録が完了しました。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method=='POST' and form.validate():
        password = form.password.data
        user = User.select_user_by_id(reset_user_id)
        with db.session.begin(subtransactions=True):
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを更新しました。')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        user = User.select_user_by_email(email)
        if user:
            with db.session.begin(subtransactions=True):
                token = PasswordResetToken.publish_token(user)
            db.session.commit()
            reset_url = f'http://127.0.0.1:5000/reset_password/{token}'
            print(reset_url)
            flash('パスワード再登録用のURLを発行しました。')
        else:
            flash('存在しないユーザです')
    return render_template('auth/forgot_password.html', form=form)

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
    return render_template('auth/user.html', form=form)

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
        return redirect(url_for('auth.user'))
    return render_template('auth/change_password.html', form=form)

# ページが見つからない場合
@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('auth.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500