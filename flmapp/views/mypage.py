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
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.utils.image_square import (
    crop_max_square
)
from flmapp.models.user import (
    User, UserInfo, Address, ShippingAddress, Credit
)
from flmapp.models.token import (
    PasswordResetToken, MailResetToken
)
from flmapp.forms.mypage import (
   ProfileForm, ChangePasswordForm, IdentificationForm, ShippingAddressForm,
   ShippingAddressRegisterForm, ShippingAddressEditForm, HiddenShippingAddressDeleteForm,
   PayWayForm, HiddenPayWayDeleteForm, CreditRegisterForm
)
from flmapp.models.trade import (
    Sell
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


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def shippingaddresses_processor():
    def search_shippingaddress(ShippingAddress_id):
        """配送先住所レコードを返す"""
        shippingaddress = ShippingAddress.search_shippingaddress(ShippingAddress_id)
        return shippingaddress
    return dict(search_shippingaddress=search_shippingaddress)


# コンテキストプロセッサ(template内で使用する関数)
@bp.context_processor
def credit_processor():
    def search_credit(Credit_id):
        """クレジット情報レコードを返す"""
        credit = Credit.search_credit(Credit_id)
        return credit
    return dict(search_credit=search_credit)


# カスタムテンプレートフィルター
@bp.app_template_filter('credit_num_format')
def credit_num_format(value):
    """クレジットカード番号下4ケタ表示フィルター"""
    return '*'*12 + str(value)[-4:]


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
        #ユーザーコードの重複チェック--------------------------
        
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
                return redirect(url_for('mypage.profile'))
        # 画像アップロード処理 ここまで--------------------------
        # データベース処理
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.user_code = form.usercode.data
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
                # パスワード更新処理
                user.password = password
            # email更新
            if mail_f == 1:
                token = MailResetToken.publish_token(user, form.email.data)
        db.session.commit()
        print(str(mail_f) + 'メールフラグ')
        if mail_f == 1:
            # メール送信処理ここから----------------------------------------------------------
            msg = Message('古書邂逅 メールアドレス変更手続きを完了してください', recipients=[email])
            msg.html = '<hr>【古書邂逅】 古書邂逅会員メールアドレス変更のお知らせ<hr>\
                        古書邂逅をご利用いただきありがとうございます。<br>\
                        以下のURLをクリックして、メールアドレス変更手続きを完了してください<br>\
                        このURLの有効期限は24時間です。<br>\
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
    if not mailResetToken:
        return redirect(url_for('route.home'))
    # mailResetToken.User_idによってユーザーを絞り込みUserテーブルのデータを取得
    user = User.select_user_by_id(int(mailResetToken.User_id))
    # データベース処理
    with db.session.begin(subtransactions=True):
        # メール更新処理
        user.email = mailResetToken.email
        # トークンレコード削除
        MailResetToken.delete_token(token)
    db.session.commit()
    return render_template('mypage/mail_reset_complete.html')

# 本人情報編集
@bp.route('/identification', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def identification():
    # ログイン中のユーザーIDによってユーザーを取得
    userinfo = UserInfo.select_userinfo_by_user_id()
    #ユーザーIDによって住所テーブルのUser_idが一致しているレコードを取得
    useradress = Address.select_address_by_user_id()
    form = IdentificationForm(request.form, pref01 = useradress.prefecture, b_year=userinfo.birth.strftime('%Y'), b_month=userinfo.birth.strftime('%m'), b_date=userinfo.birth.strftime('%d'))
    form.b_year.choices += [(i, i) for i in reversed(range(1900, datetime.date.today().year+1))]
    form.b_month.choices += [(i, i) for i in range(1, 13)]
    form.b_date.choices += [(i, i) for i in range(1, 32)]
    if request.method == 'POST' and form.validate():
        # データベース処理
        with db.session.begin(subtransactions=True):
            userinfo.last_name = form.last_name.data 
            userinfo.first_name = form.first_name.data 
            userinfo.last_name_kana = form.last_name_kana.data 
            userinfo.first_name_kana = form.first_name_kana.data 
            userinfo.birth = datetime.date(form.b_year.data, form.b_month.data, form.b_date.data)
            useradress.zip_code = form.zip01.data 
            useradress.prefecture = form.pref01.data
            useradress.address1 = form.addr01.data 
            useradress.address2 = form.addr02.data
            useradress.address3 = form.addr03.data 
        db.session.commit()
        flash('更新に成功しました')
    return render_template('mypage/identification.html', form=form, userinfo=userinfo, useradress=useradress)


@bp.route('/shippingaddress', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress():
    """配送先住所選択処理"""
    form = ShippingAddressForm(request.form, ShippingAddress_id=current_user.default_ShippingAddress_id)
    delete_form = HiddenShippingAddressDeleteForm(request.form)
    shippingaddresses = ShippingAddress.select_shippingaddresses_by_user_id()
    if shippingaddresses:
        form.ShippingAddress_id.choices += [(int(shippingaddress.ShippingAddress_id),'この住所に送る') for shippingaddress in shippingaddresses]
    if request.method=='POST' and form.validate():
        with db.session.begin(subtransactions=True):
            current_user.default_ShippingAddress_id = form.ShippingAddress_id.data
        db.session.commit()
        flash('配送先住所を設定しました。')
    return render_template('mypage/shippingaddress.html', form=form, delete_form=delete_form, shippingaddresses=shippingaddresses)


@bp.route('/shippingaddress_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress_register():
    """配送先住所登録処理"""
    form = ShippingAddressRegisterForm(request.form)
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
        # 配送先をデフォルトに設定する場合
        if form.is_default.data:
            with db.session.begin(subtransactions=True):
                current_user.default_ShippingAddress_id = shippingaddress.ShippingAddress_id
            db.session.commit()
        flash('登録しました')
        return redirect(url_for('mypage.shippingaddress'))
    return render_template('mypage/shippingaddress_register.html', form=form)

  
@bp.route('/shippingaddress_delete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress_delete():
    """配送先住所削除処理"""
    form = HiddenShippingAddressDeleteForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            # デフォルトで設定されているdefault_ShippingAddress_idが
            # 削除するShippingAddress_idと一致していればNull値に更新
            if current_user.default_ShippingAddress_id == int(form.ShippingAddress_id.data):
                current_user.default_ShippingAddress_id = None
            ShippingAddress.delete_shippingaddress(int(form.ShippingAddress_id.data))
        db.session.commit()
        flash('削除しました')
    return redirect(url_for('mypage.shippingaddress'))


@bp.route('/shippingaddress_edit/<int:shippingaddress_id>', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def shippingaddress_edit(shippingaddress_id):
    """配送先住所編集処理"""
    shippingaddress = ShippingAddress.search_shippingaddress(shippingaddress_id)
    if shippingaddress is None:
        return redirect(url_for('mypage.shippingaddress'))
    form = ShippingAddressEditForm(request.form, pref01 = shippingaddress.prefecture)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            shippingaddress.last_name = form.last_name.data 
            shippingaddress.first_name = form.first_name.data 
            shippingaddress.last_name_kana = form.last_name_kana.data 
            shippingaddress.first_name_kana = form.first_name_kana.data 
            shippingaddress.zip_code = form.zip01.data 
            shippingaddress.prefecture = form.pref01.data
            shippingaddress.address1 = form.addr01.data 
            shippingaddress.address2 = form.addr02.data
            shippingaddress.address3 = form.addr03.data 
        db.session.commit()
        flash('更新しました')
        return redirect(url_for('mypage.shippingaddress'))
    return render_template('mypage/shippingaddress_edit.html', form=form, shippingaddress=shippingaddress)


@bp.route('/pay_way', methods=['GET', 'POST'])
@login_required
def pay_way():
    """支払い方法選択処理"""
    if current_user.default_pay_way == 1:
        default_pay_way = 0
    elif current_user.default_pay_way == 2:
        default_pay_way = current_user.default_Credit_id
    form = PayWayForm(request.form, pay_way=default_pay_way)
    delete_form = HiddenPayWayDeleteForm(request.form)
    credits = Credit.select_credits_by_user_id()
    if credits:
        form.pay_way.choices += [(credit.Credit_id, 'クレジットカード') for credit in credits]
    if request.method=='POST' and form.validate():
        # 代金引き換えのvalue:0に設定済み(1だとCredit_idと重複し判断できないため)
        if form.pay_way.data == 0:
            # デフォルト設定を代金引き換えに更新
            with db.session.begin(subtransactions=True):
                current_user.default_pay_way = 1
                # デフォルト設定ですでにdefault_Credit_idが設定されていればNull値に更新
                if current_user.default_Credit_id:
                    current_user.default_Credit_id = None
            db.session.commit()
        else:
            # デフォルト設定をクレジットに更新
            with db.session.begin(subtransactions=True):
                current_user.default_pay_way = 2
                current_user.default_Credit_id = int(form.pay_way.data)
            db.session.commit()
        flash('支払い方法を選択しました。')
    return render_template('mypage/pay_way.html', form=form, credits=credits, delete_form=delete_form)

@bp.route('/pay_way_delete', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def pay_way_delete():
    """支払い方法削除処理"""
    form = HiddenPayWayDeleteForm(request.form)
    if request.method == 'POST':
        with db.session.begin(subtransactions=True):
            # デフォルトで設定されているdefault_Credit_idが
            # 削除するdefault_Credit_idと一致していればNull値に更新し
            # default_pay_wayを1(代金引換)に更新する
            if current_user.default_Credit_id == int(form.Credit_id.data):
                current_user.default_pay_way = 1
                current_user.default_Credit_id = None
            Credit.delete_credit(int(form.Credit_id.data))
        db.session.commit()
        flash('削除しました')
    return redirect(url_for('mypage.pay_way'))


@bp.route('/credit_register', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def credit_register():
    """クレジットカード登録"""
    form = CreditRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        credit = Credit(
            # ユーザーID
            User_id = user_id,
            # クレジット名義人
            credit_name = form.credit_name.data,
            # クレジットカード番号
            credit_num = form.credit_num.data,
            # クレジット有効期限 Date型のため、日付はすべて1に設定するとする。
            expire = datetime.date(form.expiration_date02.data, form.expiration_date01.data, 1)
        )
        credit.security_code = str(form.security_code.data)
        # データベース処理
        with db.session.begin(subtransactions=True):
            credit.create_new_credit()
        db.session.commit()
        # デフォルトに設定する場合
        if form.is_default.data:
            with db.session.begin(subtransactions=True):
                current_user.default_pay_way = 2
                current_user.default_Credit_id = credit.Credit_id
            db.session.commit()
        flash('登録しました')
        return redirect(url_for('mypage.pay_way'))
    return render_template('mypage/credit_register.html', form=form)


@bp.route('/logout', methods=['GET', 'POST'])
@login_required # ログインしていないと表示できないようにする
def logout():
    return render_template('mypage/logout.html')
