## SQLAlqhemyの基本操作
### トランザクションを利用してデータを更新
処理の中でエラーがあった場合には、DBは更新されずロールバックする。
```
with db.session.begin(subtransactions = True):
    処理
db.session.commit()
```

### データの挿入
```
db.session.add() #単一のレコードの挿入
db.session.add_all([]) #複数のレコードの挿入
```

### データの削除
`db.session.delete() #単一のレコードの削除`

### データの取り出し
```
Table.query.get(1) #主キーで絞り込んで取り出し
Table.query.all() #データを全てリストにして取り出し
Table.query.first() #データの最初の要素だけを取り出し
```

### データの絞り込み
```
Table.query.filter_by(name = 'A') #カラムnameがAのデータのみに絞り込み
Table.query.filter(Table.age > 10) #カラムageが10よりも大きいもののみ絞り込み
Table.query.filter(Table.name.startswith('A')) #カラムnameがaで始まるもののみ絞り込み
Table.query.filter(Table.name.endswith('A')) #カラムnameがaで終わるもののみ絞り込み
Table.query.limit(1) #limitで指定した分だけ件数を絞り込む
```

### データの更新
```
user_name = session.query(User).filter(User.id==1).first()
user_name.name = '太郎'
session.commit()
```
User.idが1のユーザの名前を更新する。
user_name = User
session.commit()でクエリ実行

### 参考

https://qiita.com/ariku/items/75799665acd09520bed2

https://qiita.com/tomo0/items/a762b1bc0f192a55eae8