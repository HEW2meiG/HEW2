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
    LoginForm, RegisterForm, CreateUserForm, ForgotPasswordForm, ResetPasswordForm
)

from flmapp import mail # メール送信時インポート
from flask_mail import Mail, Message # メール送信時インポート

bp = Blueprint('auth', __name__, url_prefix='/auth')

# ログアウト
@bp.route('/logout')
def logout():
    logout_user() # ログアウト
    return redirect(url_for('route.home'))

# ログイン
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
        # ユーザーが存在するかつ、ユーザーのis_activeがTrue(有効)かつ、ユーザーが入力したパスワードがユーザーのパスワードと一致する
        if user and user.is_active and user.validate_password(form.password.data):
            # ユーザーをログインさせる remember:セッションの期限が切れた後にユーザーを記憶する(ログインが維持される)
            login_user(user, remember=True)
            # request.args.get（）；GETリクエストで引数を受け取る
            next = request.args.get('next')
            if not next:
                next = url_for('route.home')
            return redirect(next)
        # ユーザーが存在しない
        elif not user:
            flash('存在しないユーザです')
        # ユーザーが有効でない
        elif not user.is_active:
            flash('無効なユーザです。パスワードを再設定してください')
        # パスワードが違う
        elif not user.validate_password(form.password.data):
            flash('メールアドレスとパスワードの組み合わせが誤っています')
    return render_template('auth/login.html', form=form)

# ユーザー仮登録
@bp.route('/mailregister', methods=['GET', 'POST'])
def register():
    form = CreateUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email = form.email.data
        )
        # データベースにユーザー情報登録
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        token = ''
        # データベースにパスワードリセットトークンを登録
        with db.session.begin(subtransactions=True):
            token = PasswordResetToken.publish_token(user)
        db.session.commit()
        # メール送信処理ここから----------------------------------------------------------
        msg = Message('古書邂逅 仮登録メール', recipients=[user.email])
        msg.html = '<hr>【古書邂逅】 古書邂逅会員仮登録完了のお知らせ<hr>\
                    この度は、古書邂逅会員にご登録いただきまして誠にありがとうございます。<br>\
                    下記ページアドレス(URL)をクリックすることで、本登録が完了となります。<br>\
                    <br><br>\
                    【ご登録されたメールアドレス】<br>\
                    {email}<br>\
                    【こちらをクリックして本登録を完了してください】<br>\
                    {url}'.format(email=user.email,url=url_for('auth.userregister', token=token, _external=True))
        mail.send(msg)
        # メール送信処理ここまで----------------------------------------------------------
        # デバッグ用---------------------------------------------------------------
        print(
            f'本登録URL: http://127.0.0.1:5000/auth/userregister/{token}'
        )
        # デバッグ用---------------------------------------------------------------
        flash('本登録用のURLをお送りしました。ご確認ください')
        return redirect(url_for('auth.login'))
    return render_template('auth/create_user.html', form=form)

# ユーザー本登録
@bp.route('/userregister/<uuid:token>', methods=['GET', 'POST'])
def userregister(token):
    form = RegisterForm(request.form)
    # トークンによってユーザーIDを取得する
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        # ユーザーIDが取得できない場合
        abort(500)
    if request.method=='POST' and form.validate():
        password = form.password.data
        # reset_user_idによってユーザーを絞り込みUserテーブルのデータを取得
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
        # データベース登録処理
        with db.session.begin(subtransactions=True):
            # トークンレコード削除
            PasswordResetToken.delete_token(token)
            # パスワード更新処理(パスワードのハッシュ化とユーザーの有効化)
            user.save_new_password(password)
            # Userテーブルusername更新
            user.username = form.username.data
            # UserInfoテーブルにレコードの挿入
            userinfo.create_new_userinfo()
            # Adressテーブルにレコードの挿入
            address.create_new_useraddress()
            # Userテーブルpicture_path更新
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
        flash('新規会員登録が完了しました。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# パスワードを忘れた人はこちら
@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        # emailによってユーザーを絞り込みUserテーブルのデータを取得
        user = User.select_user_by_email(email)
        # ユーザーが存在する場合パスワードのトークンを発行する
        if user:
            #パスワードリセットトークン情報テーブルにレコードの挿入
            with db.session.begin(subtransactions=True):
                token = PasswordResetToken.publish_token(user)
            db.session.commit()
            # メール送信処理ここから----------------------------------------------------------
            msg = Message('古書邂逅 パスワード再設定メール', recipients=[user.email])
            msg.html = '<hr>【古書邂逅】 パスワード再設定のご案内<hr>\
                        いつも古書邂逅をご利用頂き、誠にありがとうございます。<br>\
                        パスワード変更のリクエストを受け付けました。<br>\
                        下記ページアドレス(URL)をクリックしてパスワードの再設定を行ってください。<br>\
                        再設定を行うまではパスワードは変更されません。<br>\
                        <br><br>\
                        【こちらをクリックしてパスワードの再設定を行ってください】<br>\
                        {url}'.format(url=url_for('auth.reset_password', token=token, _external=True))
            mail.send(msg)
            # メール送信処理ここまで----------------------------------------------------------
            # デバッグ用---------------------------------------------------------------
            print(
                f'パスワード再設定用URL: http://127.0.0.1:5000/auth/reset_password/{token}'
            )
            # デバッグ用---------------------------------------------------------------
            flash('パスワード再登録用のURLを発行しました。')
        else:
            flash('存在しないユーザです')
    return render_template('auth/forgot_password.html', form=form)

# パスワード再設定
@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    # トークンに紐づいたユーザーIDを得る
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        abort(500)
    if request.method=='POST' and form.validate():
        password = form.password.data
        # reset_user_idによってユーザーを絞り込みUserテーブルのデータを取得
        user = User.select_user_by_id(reset_user_id)
        # データベース処理
        with db.session.begin(subtransactions=True):
            # パスワード更新処理(パスワードのハッシュ化とユーザーの有効化)
            user.save_new_password(password)
            # トークンレコード削除
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを再設定しました。')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)