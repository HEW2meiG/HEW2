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
    PasswordResetToken
)
from flmapp.forms.mypage import (
   ProfileForm, ChangePasswordForm, IdentificationForm,ShippingAddressForm
)

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
        password = form.password.data
        # データベース処理
        with db.session.begin(subtransactions=True):
            # email更新
            #! メールにURL送信、URLをクリックして更新
            user.email = form.email.data
            if password:
                # パスワード更新処理(パスワードのハッシュ化とユーザーの有効化)
                user.save_new_password(password)
        db.session.commit()
        flash('更新に成功しました')
    return render_template('mypage/mail_password.html', form=form)

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
