import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,
    current_app as app #Blueprint環境下で、設定値(config)を取得
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User, UserInfo, Address, ShippingAddress, Credit
)
from flmapp.models.token import (
    PasswordResetToken, MailResetToken
)
from flmapp.forms.mypage import (
   ProfileForm, ChangePasswordForm, IdentificationForm,ShippingAddressForm
)

from flmapp import mail # メール送信インポート
from flask_mail import Mail, Message # メール送信インポート

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

# 画像アップロード処理用関数 ここから--------------------------------------
def allowed_image(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]
#ここまで------------------------------------------------------------------

@bp.route('/')
@login_required # login_requiredを追加するとログインしていないとアクセスができないようになる
def mypagetop():
    return render_template('mypage/mypage.html')

# プロフィール設定
@bp.route('/profile', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def profile():
    form = ProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        # ログイン中のユーザーIDによってユーザーを取得
        user = User.select_user_by_id(current_user.get_id())
        # 画像アップロード処理 ここから--------------------------
        imagename = ''
        image = request.files[form.picture_path.name]
        if image:
            # 画像アップロード処理用関数
            if allowed_image(image.filename):
                # ファイル名から拡張子を取り出す
                ext = image.filename.rsplit('.', 1)[1]
                # imagenameはユーザーID+現在の時間+.拡張子
                imagename = str(user.User_id) + '_' + \
                            str(int(datetime.now().timestamp())) + '.' + ext
                # ファイルの保存
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], imagename))
            else:
                flash('画像のアップロードに失敗しました。')
                return redirect(url_for('mypage.profile'))
        # 画像アップロード処理 ここまで--------------------------
        # データベース処理
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.prof_comment = form.prof_comment.data
            if imagename: # imagenameが設定されていれば(画像があれば)更新する
                user.picture_path = imagename
        db.session.commit()
        flash('プロフィール情報を更新しました。')
    return render_template('mypage/profile.html', form=form)

# パスワード・メール変更
@bp.route('/mail_password', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def mail_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        # ログイン中のユーザーIDによってユーザーを取得
        user = User.select_user_by_id(current_user.get_id())
        pass_f = 0
        mail_f = 0
        # パスワードの変更フラグ
        if not form.now_password.data == '':
            now_password = form.now_password.data
            # 現在のパスワードチェック
            if user.validate_password(now_password):
                password = form.password.data
                pass_f =1
            else:
                flash('現在のパスワードが誤っています。')
        # emailの変更フラグ
        if not user == User.select_user_by_email(form.email.data):
            token = ''
            email = form.email.data
            mail_f = 1
        # データベース処理
        with db.session.begin(subtransactions=True):
            # パスワード更新
            if pass_f == 1:
                # パスワード更新処理(パスワードのハッシュ化とユーザーの有効化)
                user.save_new_password(password)
            # email更新
            if mail_f == 1:
                token = MailResetToken.publish_token(user, form.email.data)
        db.session.commit()
        print(str(mail_f) + 'メールフラグ')
        if mail_f == 1:
            # メール送信処理ここから----------------------------------------------------------
            msg = Message('古書邂逅 仮登録メール', recipients=[user.email])
            msg.html = '<hr>【古書邂逅】 古書邂逅会員メールアドレス変更のお知らせ<hr>\
                        この度は、古書邂逅会員にご登録いただきまして誠にありがとうございます。<br>\
                        下記ページアドレス(URL)をクリックして登録を完了させてください。<br>\
                        <br><br>\
                        【ご登録されたメールアドレス】<br>\
                        {email}<br>\
                        【こちらをクリックして登録を完了させてください。】<br>\
                        {url}'.format(email=email,url=url_for('mypage.mail_reset_complete', token=token, _external=True))
            mail.send(msg)
            # メール送信処理ここまで----------------------------------------------------------
            # デバッグ用---------------------------------------------------------------
            print('*'*120)
            print(
                f'本登録URL: http://127.0.0.1:5000/mypage/mail_reset_complete/{token}'
            )
            # デバッグ用---------------------------------------------------------------
            flash(email + 'にURLを送信しました。URLをクリックするとメールアドレスの登録が完了します。')
        elif pass_f == 1:
            flash('更新に成功しました')
        else:
            flash('変更するメールアドレスまたはパスワードを入力してください')
    return render_template('mypage/mail_password.html', form=form)

# メール再設定
@bp.route('/mail_reset_complete/<uuid:token>', methods=['GET', 'POST'])
def mail_reset_complete(token):
    # トークンに紐づいたユーザーIDを得る
    mailResetToken = MailResetToken.get_user_id_by_token(token)
    # user = User.select_user_by_id(current_user.get_id())
    if not mailResetToken:
        abort(500)
    
    # MailResetTokenテーブルのemailデータを取得
    # email = mailResetToken.email

    # mailResetToken.User_idによってユーザーを絞り込みUserテーブルのデータを取得
    user = User.select_user_by_id(int(mailResetToken.User_id))
    # データベース処理
    with db.session.begin(subtransactions=True):
        # メール更新処理
        user.email = mailResetToken.email
        # トークンレコード削除
        MailResetToken.delete_token(token)
    db.session.commit()
    flash('メールを再設定しました。')
    return redirect(url_for('auth.login'))
    return render_template('mypage/mail_reset_complete.html')

# 本人情報編集
@bp.route('/identification', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def identification():
    # ログイン中のユーザーIDによってユーザーを取得
    userinfo = UserInfo.select_userinfo_by_user_id()
    #ユーザーIDによって住所テーブルのUser_idが一致しているレコードを取得
    useradress = Address.select_address_by_user_id()
    form = IdentificationForm(request.form, pref01 = useradress.prefecture)
    if request.method == 'POST' and form.validate():
        # データベース処理
        with db.session.begin(subtransactions=True):
            userinfo.last_name = form.last_name.data 
            userinfo.first_name = form.first_name.data 
            userinfo.last_name_kana = form.last_name_kana.data 
            userinfo.first_name_kana = form.first_name_kana.data 
            userinfo.birth = form.birth.data 
            useradress.zip_code = form.zip01.data 
            useradress.prefecture = form.pref01.data
            useradress.address1 = form.addr01.data 
            useradress.address2 = form.addr02.data
            useradress.address3 = form.addr03.data 
        db.session.commit()
        flash('更新に成功しました')
    return render_template('mypage/identification.html', form=form, userinfo=userinfo, useradress=useradress)

# 発送元・お届け先住所一覧
@bp.route('/shippingaddress', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress():
    form = ShippingAddressForm(request.form)
    return render_template('mypage/shippingaddress.html', form=form)

# 発送元・お届け先住所登録
@bp.route('/shippingaddress_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress_register():
    form = ShippingAddressForm(request.form)
    if request.method == 'POST' and form.validate():
        userid = current_user.get_id()
        shippingaddress = ShippingAddress(
            User_id = userid,
            last_name = form.last_name.data,
            first_name = form.first_name.data,
            last_name_kana = form.last_name_kana.data,
            first_name_kana = form.first_name_kana.data,
            zip_code = form.zip01.data,
            prefecture = form.pref01.data,
            address1 = form.addr01.data,
            address2 = form.addr02.data,
            address3 = form.addr03.data
        )
        # データベース登録処理
        with db.session.begin(subtransactions=True):
            shippingaddress.create_new_shippingaddress()
        db.session.commit()
        flash('登録に成功しました')
    return render_template('mypage/shippingaddress_register.html', form=form)
