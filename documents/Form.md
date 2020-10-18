# Form
## FormのField一覧
|||
|:------|:------|
|StringField|文字列の入力(`<input tyape='text'>`)|
|TextAreaField|テキストエリア(`<textarea>`)|
|DateField|日付を扱う|
|DateTimeField|タイムスタンプを扱う|
|BooleanField|真偽値を扱う(checkbox)|
|FileField|アップロードするファイルを扱う|
|DecimalField|Decimal型を扱う|
|FloatField|不動小数点数を扱う|
|IntegerField|数値型を扱う|
|RadioField|ラジオボタンを扱う|
|SelectMultipleField|セレクトボックスを扱う|
|FormField|他のフォームに埋め込んで利用する|
|HiddenField|hidden要素を扱う|
|PasswordField|パスワードを扱う|
|SubmitField|送信ボタンを扱う|

## FormのField詳細
### テキストボックスの長さの変更
`{{ form.field(siza=〇〇) }}`

`{{ render_field(form.field, size=12) }}`

### デフォルト値

画面に入力するデフォルトの値を設定する

`name = StringField('名前：',default='Flask太郎')`

チェックボックスでデフォルトはチェックする

`{{ form.field(checked=True) }}`

`{{ render_field(form.field,checked=True) }}`

### プレースホルダー
ユーザーが入力しやすくなるように入力フォーム上に仮の値を薄く表示させること
オプションとして、render_kw={"placeholder":"〇〇"}を追加する

`birthday = DataField('誕生日:',format='%Y/%m/%d',render_kw={"placeholder":"年/月/日"})`

### クラスの追加
`{{ form.field(class="〇〇") }}`

`{{ render_field(form.field, class="〇〇") }}`

## バリデーション
### バリデーションチェック

`from wtforms.validators import DataRequired`

fieldで以下のように記載する。

`StringField(validators=[DataRequires('データを入力してください')])`

### 代表的なバリデータ

|||
|:------|:------|
|DataRequired|データが入っていない場合にエラーとして値を返す|
|Email|メール型でないと入力できなくする。(pip install wtform[email])|
|EqualTo|他のフィールドと等しいか確認する|
|Length|文字列の長さを指定する|
|NumberRange|数値の大きさの範囲を指定する|


### 単体のバリデーターの自作

以下の関数をクラス内に作成してフィールドごとにバリデーションをする。

```
def validate_フィールド名(form,field):
    if field.data == '':
        raise ValidationError('エラー')
        #reise:自作した関数などで例外を発生させたい場合
```

クラスの外に自作関数を作った場合は、validatorsのところで指定する

`validators=[自作関数]`

### 複数のフィールドをバリデーションしたい場合(validate関数の上書き)
```
def validate(self):
    if not super(Form,self).validate():
        return False
    ...バリデーションを追加(問題がある場合にはFalseを返すようにする)
```

### フラッシュメッセージの表示（flask.flash）
`flash('メッセージ'),{% for message in get_flashed_messages() %}{{ message }}{% endfor %}`
