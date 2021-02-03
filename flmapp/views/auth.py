import os
import glob # 画像のリサイズ
import datetime
from PIL import Image # 画像のリサイズ
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, 
    current_app as app #Blueprint環境下で、設定値(config)を取得
)
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.utils.image_square import (
    crop_max_square
)
from flmapp.models.user import (
    User, UserInfo, Address
)
from flmapp.models.token import (
    UserTempToken, PasswordResetToken
)
from flmapp.forms.auth import (
    LoginForm, RegisterForm, CreateUserForm, ForgotPasswordForm, ResetPasswordForm
)

from flmapp import mail # メール送信インポート
from flask_mail import Mail, Message # メール送信インポート

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 画像アップロード処理用関数 ここから--------------------------------------
def allowed_image(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]
#ここまで------------------------------------------------------------------

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
        email = form.email.data
        # ユーザー仮登録トークン情報テーブルにメールアドレスを登録
        with db.session.begin(subtransactions=True):
            token = UserTempToken.publish_token(email)
        db.session.commit()
        # メール送信処理ここから----------------------------------------------------------
        msg = Message('古書邂逅 仮登録メール', recipients=[email])
        msg.html = '<hr>【古書邂逅】 古書邂逅会員仮登録完了のお知らせ<hr>\
                    この度は、古書邂逅会員にご登録いただきまして誠にありがとうございます。<br>\
                    下記ページアドレス(URL)から会員登録をしてください。<br>\
                    <br><br>\
                    【ご登録されたメールアドレス】<br>\
                    {email}<br>\
                    【こちらから本登録を行ってください】<br>\
                    {url}'.format(email=email,url=url_for('auth.userregister', token=token, _external=True))
        # mail.send(msg)
        # メール送信処理ここまで----------------------------------------------------------
        # デバッグ用---------------------------------------------------------------
        print('*'*120)
        print(
            f'本登録URL: http://127.0.0.1:5000/auth/userregister/{token}'
        )
        print('*'*120)
        # デバッグ用---------------------------------------------------------------
        flash('本登録用のURLをお送りしました。ご確認ください')
        return redirect(url_for('route.home'))
    return render_template('auth/create_user.html', form=form)

# ユーザー本登録
@bp.route('/userregister/<uuid:token>', methods=['GET', 'POST'])
def userregister(token):
    form = RegisterForm(request.form)
    form.b_year.choices += [(i, i) for i in reversed(range(1900, datetime.date.today().year+1))]
    form.b_month.choices += [(i, i) for i in range(1, 13)]
    form.b_date.choices += [(i, i) for i in range(1, 32)]
    email = UserTempToken.get_email_by_token(token)
    if not email:
        return redirect(url_for('route.home'))
    if request.method=='POST' and form.validate():
        # Userインスタンス作成
        user = User(
            user_code = form.user_code.data,
            username = form.username.data,
            email = email
        )
        user.password = form.password.data
        # データベース登録処理
        with db.session.begin(subtransactions=True):
            #Userテーブルにレコードの挿入
            User.create_new_user(user)
        db.session.commit()
        # 画像アップロード処理 ここから-------------------------------------------------
        imagename = ''
        image = request.files[form.picture_path.name]
        if image:
            # 画像アップロード処理用関数
            if allowed_image(image.filename):
                # ファイル名から拡張子を取り出す
                ext = image.filename.rsplit('.', 1)[1]
                # imagenameはユーザーID+現在の時間+.拡張子
                imagename = str(user.User_id) + '_' + \
                            str(int(datetime.datetime.now().timestamp())) + '.' + ext
                # ファイルの保存
                image.save(os.path.join(app.config["ORIGINAL_IMAGE_UPLOADS"], imagename))
                im = Image.open(os.path.join(app.config["ORIGINAL_IMAGE_UPLOADS"], imagename))
                # 最大サイズの正方形に切り出したあと、200に縮小
                im_thumb = crop_max_square(im).resize((200, 200), Image.LANCZOS)
                # ファイルの保存
                im_thumb.save(os.path.join(app.config["IMAGE_UPLOADS"], imagename))
            else:
                flash('画像のアップロードに失敗しました。')
                return redirect(url_for('auth.userregister', token=token))
        # 画像アップロード処理 ここまで--------------------------------------------------
        userinfo = UserInfo(
            User_id = user.User_id,
            last_name = form.last_name.data,
            first_name = form.first_name.data,
            last_name_kana = form.last_name_kana.data,
            first_name_kana = form.first_name_kana.data,
            birth = datetime.date(form.b_year.data, form.b_month.data, form.b_date.data)
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
            # UserInfoテーブルにレコードの挿入
            userinfo.create_new_userinfo()
            # Adressテーブルにレコードの挿入
            address.create_new_useraddress()
            #TODO: コメントアウトをけしてください
            if imagename:
                user.picture_path = imagename
            #TODO: トークンレコード削除を削除するクラスメソッドを以下に追加してください
            UserTempToken.delete_token(token)
        db.session.commit()
        flash('新規会員登録が完了しました。')
        login_user(user, remember=True)
        return redirect(url_for('route.home'))
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
            return redirect(url_for('auth.login'))
        else:
            flash('存在しないユーザです。')
    return render_template('auth/forgot_password.html', form=form)

# パスワード再設定
@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    # トークンに紐づいたユーザーIDを得る
    reset_user_id = PasswordResetToken.get_user_id_by_token(token)
    if not reset_user_id:
        return redirect(url_for('route.home'))
    if request.method=='POST' and form.validate():
        password = form.password.data
        # reset_user_idによってユーザーを絞り込みUserテーブルのデータを取得
        user = User.select_user_by_id(reset_user_id)
        # データベース処理
        with db.session.begin(subtransactions=True):
            user.password = password
            # トークンレコード削除
            PasswordResetToken.delete_token(token)
        db.session.commit()
        flash('パスワードを再設定しました。')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)