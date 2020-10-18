## flask-mail
### flask-mailをインストール
仮装環境の有効化

`conda env list`

`conda activate flaskenv`

flask-mailのインストール

`pip install flask-mail`
　
### 設定はflmapp/__init__に記述済み
```
from flask_mail import Mail, Message
mail = Mail()
```
```
app.config['DEBUG'] = True # デバッグのサポート
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'koshokaikou.official@gmail.com'
app.config['MAIL_PASSWORD'] = 'tegjmwoizirebndj'
app.config['MAIL_DEFAULT_SENDER'] = 'koshokaikou.official@gmail.com'
app.config['MAIL_MAX_EMAILS'] = 5 #送信するメールの最大数
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHHMENTS'] = False

mail.init_app(app)
```
### 備考
メールアドレス:koshokaikou.official@gmail.com

パスワード:hew2shimomuraG

アプリパスワード:tegjmwoizirebndj

注意)

アプリパスワードを設定しないとグーグルからブロックされてしまう。

設定方法は、グーグルの設定画面から、2段階認証をオンにして、[Google へのログイン]

### viewファイルに下記をインポートする
```
from flmapp import mail # メール送信インポート
from flask_mail import Mail, Message # メール送信インポート
```
### viewファイルにメール送信処理を追加する
```
# メール送信処理ここから----------------------------------------------------------
msg = Message('件名', recipients=[user.email])
msg.html = '本文(html形式)'
mail.send(msg)
# メール送信処理ここまで----------------------------------------------------------
```
recipients=['送信するメールアドレス']
