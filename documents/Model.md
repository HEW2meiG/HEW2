## Model
### テーブルの作成
```
class User(db.Model): # PythonではUserというクラスのインスタンスとしてデータを扱います
    __tablename__ = 'User'  # テーブル名は User です
    id = Column(Integer, primary_key=True, unique=True)  # 整数型のid をprimary_key として、被らないようにします
    email = Column(String)  # 文字列の emailというデータを作ります
    name = Column(String)  # 文字列の nameというデータを使います
```
`__tablename__='entries'`:実際のデータベースに格納されるテーブルの名前

### カラムにオプション一覧
|オプション|制約|使用例|
|:------|:------|:------|
|primary_key|主キー制約<br>(ユニーク＋NOT NULL＋インデックス)|`db.Column(db.Integer,primary_key=True)`|
|unique|ユニーク制約<br>(同じ値を入れられない)|`db.Column(db.Integer,unique=True)`|
|nullable|NOT NULL制約<br>(NULL値を入れられない)|`db.Column(db.Integer,nullable=False)`|
|CheckConstraint|チェック制約<br>(自由に制約を作成する)|`__table_args__ = (CheckConstraint('update_at > create_at'),)`|
|index|インデックスを作成<br>（索引。検索の際に高速化できる）|`db.Column(db.Text,index=True)`|
|db.Index|インデックスを作成|`db.Index("some_index",func.lower(Person.name))#関数インデックス`|
|server_default|デフォルト値の追加|`db.Column(db.Text,server_default=A)`|

### マイグレーション
#### マイグレーションとは
プログラムのコードからデータベースにテーブルを作成・編集すること
### マイグレーションの手順
#### 注意
viewファイルにモジュールをインポートしておく
```
from flmapp.models.〇〇 import (
    〇〇
)
```
#### 仮装環境の有効化
`conda env list`

`conda activate flaskenv`

#### データベースの設定を記載してるファイルを設定
mac

`export FLASK_APP=setup.py`


windows

`set FLASK_APP=setup.py`
#### データベースの変更・追加は以下の手順
##### テーブルの設定を記載したファイルの内容をmigrationsフォルダに反映する
some message部分にコメントを入れる

`flask db migrate -m "some message"`
##### フォルダの内容をDBに登録する
`flask db upgrade`