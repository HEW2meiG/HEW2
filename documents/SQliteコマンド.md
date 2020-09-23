## SQliteコマンド一覧
### SQliteデータベース接続方法
cd カレントフォルダ(HEW2)に移動する
`sqlite3 data.sqlite`
### SQliteデータベース接続終了
`.exit`
### テーブル定義を確認
`.schema テーブル名`
### テーブル一覧を確認
`.tables`
### SQLを実行
`select * from テーブル名;`
### テーブルを削除する
`DROP TABLE テーブル名;`
### テーブルのデータを削除する
`DELETE FROM テーブル名 WHERE 条件式;`