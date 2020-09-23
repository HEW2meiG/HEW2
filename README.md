## GitHub 使い方


### 0.cd カレントフォルダに移動する

### 1.masterブランチからブランチを作成

`git branch`

（masterブランチにいるか確認する）

`git pull origin master`

(ローカルのmasterブランチをpullで更新)

`git checkout -b <新ブランチ名>`

### 2.自分のファイルに追加する

### 3.ステージに追加し、コミット
`git add ファイル名`

複数ファイルを登録したい時は半角スペースを開ける

`git status`

（現在の状況を確認する）

`git commit -m "コミットメッセージ"`

`git status`

（現在の状況を確認する）

### 4.ブランチをGitHubにプッシュ
`git push origin <ブランチ名>`

### 開発が終了するまで2~4繰り返し（定期的にプッシュする）

### 5.開発が完了したらプルリクエストを出す
**Compare & pull request**をクリック

リーダー:File changedタブから変更内容をチェック

#### OK

**Merge pull request**ボタンを押しmasterブランチにマージ

**Delete branch**ボタンを押し不要になったリモートブランチを削除

6へ

#### NO
2に戻る

### 6.ローカルブランチを削除する
`git checkout master`

`git branch -D <ブランチ名>`

### 7.ローカルのmasterブランチをpullで更新
`git branch`

（masterブランチにいるか確認する）

`git pull origin master`

### 1に戻る