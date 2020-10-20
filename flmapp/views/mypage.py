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

from flmapp.models.auth import (
    User, UserInfo, Address, PasswordResetToken
)
from flmapp.models.mypage import (
    ShippingAddress, Credit
)
from flmapp.forms.mypage import (
   ProfileForm, ChangePasswordForm, IdentificationForm
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
        # 画像ファイルがあった場合
        if request.files:
            image = request.files[form.picture_path.name]
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
    form = IdentificationForm(request.form)
    if request.method == 'POST' and form.validate():
        # ログイン中のユーザーIDによってユーザーを取得
        user = User.select_user_by_id(current_user.get_id())
        # データベース処理
        #with db.session.begin(subtransactions=True):

        #db.session.commit()
        #flash('更新に成功しました')
    return render_template('mypage/identification.html', form=form)