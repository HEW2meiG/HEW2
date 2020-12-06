## GitHub 使い方

### 約束事
* masterブランチで作業をしない。作業は必ず自分のブランチをきってから行う。
* マージ(Merge)はリーダーが行う。
* `git push origin master`をしない。

### 0.cd カレントフォルダ(HEW2)に移動する

### 1.masterブランチからブランチを作成

`git branch`

（masterブランチにいるか確認する）

`git pull origin master`

(ローカルのmasterブランチをpullで更新)

`git checkout -b 新ブランチ名(自分の名字)`

`git branch`

（自分のブランチにいるか確認する）

### 2.開発

### 3.ステージに追加し、コミット

`git status`

git add するファイル(自分の担当ファイルのみか)を確認する。

**data.sqliteが合った場合は以下のコマンドを打つ！**

`git restore data.sqlite`

`git status`

（現在の状況をもう一度確認し、余計なファイルがないか再確認）

`git add .`

`git status`

（現在の状況を確認する）

`git commit -m "コミットメッセージ"`

`git status`

（現在の状況を確認する）

### 4.ブランチをGitHubにプッシュ
`git push origin ブランチ名(自分の名字)`

### 開発が終了するまで2~4繰り返し（定期的にプッシュする）

### 5.開発が完了したらプルリクエストを出す
**Compare & pull request**をクリック

**Merge pull requestボタンは押さない！！！**

#### 以下は必ずリーダーのみ行う
<details>
Merge pull requestボタンを押しmainブランチにマージ

Delete branchボタンを押し不要になったリモートブランチを削除
</details>

### 6.ローカルブランチを削除する
`git checkout master`

`git branch -D ブランチ名(自分の名前)`

### 7.ローカルのmasterブランチをpullで更新
`git branch`

（masterブランチにいるか確認する）

`git pull origin master`

### 1に戻る
