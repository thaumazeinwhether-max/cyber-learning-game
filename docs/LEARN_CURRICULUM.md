# Phase 1「Learn」正式カリキュラム

## 1. 位置付けと目的

Phase 1「Learn」は、Phase 2「Build」と Phase 3「Attack & Defend」で必要となる基本的な新規学習を、ほぼ完了させる段階である。初心者が正しく理解し、知識を使えるように定着させることを、学習時間の短さより優先する。

学習の舞台は「Cyber Defense Academy / サイバー防衛学校」とする。各小単元は **教材 → 通常戦 → 次の教材 → 通常戦 → … → BOSS** の流れで進める。独立した復習問題や前提確認テストは設けない。理解が必要な箇所では通常戦やBOSSの問題数を増やす。

この文書はPhase 1全体の正式な学習範囲と出題方針を定める。`docs/MVP_V0_1.md` の4テーマは、小さく動かして検証する初期MVPの範囲であり、正式カリキュラム全体の代わりではない。現行アプリの教材・問題も正式カリキュラムの実装完了を意味しない。詳細な教材本文、個別問題、画面実装は別途段階的に決める。

## 2. 正式な訓練順序

以下の01から12までを順に学ぶ。各訓練の最後にBOSSを置く。12のBOSSはLearnフェーズ全体のFINAL BOSSを兼ねる。

### 01 コンピュータ・OS基礎訓練

- コンピュータの基本構成：CPU、メモリ、ストレージ、入出力装置
- OSとは
- OSとアプリケーション
- ファイル・フォルダ・拡張子
- ファイル形式
- パス、絶対パス、相対パス
- ディレクトリ構造
- プログラムとプロセス
- GUI / CLI
- ターミナル・PowerShellの基本的な役割
- 最後にBOSS

### 02 Python基礎Ⅰ訓練

- Pythonとプログラム
- `print`
- 変数
- 文字列、整数、小数、真偽値
- 算術演算子、比較演算子、論理演算子
- `if`、`elif`、`else`
- 最後にBOSS

### 03 ネットワーク基礎訓練

- ネットワークとは
- LAN、WAN、インターネット
- IPアドレス、IPv4の基本
- ルーター、デフォルトゲートウェイ
- DNS、ポート番号
- TCP、UDP、TCPとUDPの違い
- 通信が相手に届くまでの基本的な流れ
- 最後にBOSS

### 04 Web・HTTP基礎訓練

- Webとは
- クライアント、サーバー、Webブラウザ
- URL、ドメイン
- HTTP、HTTP Request、HTTP Response
- GET、POST
- HTTP Status Code：200、3xx、4xx、5xx
- HTTP Header、HTTP Body
- Cookie、Session
- HTML / CSS / JavaScriptの役割
- 最後にBOSS

### 05 Python基礎Ⅱ訓練

- `for`、`range`、`while`
- `list`、listの追加・参照
- `dict`
- 関数、引数、戻り値
- 変数スコープの超基礎
- module、`import`
- 例外、`try / except`
- エラーメッセージ、デバッグ
- 最後にBOSS

### 06 Web制作基礎訓練

- HTMLとは、HTML文書構造
- 見出し・段落、リンク、画像、リスト
- フォーム、`input`、`button`
- CSSとは、セレクタ
- 色、文字、余白、レイアウト基礎
- JavaScriptの役割、DOMの超基礎
- ユーザー入力と画面表示の関係
- 最後にBOSS

### 07 Flask・Webアプリ基礎訓練

- Webフレームワーク、Flask
- Flaskアプリの基本構造
- Route、URLとRoute
- Template、Jinjaの基本
- Staticファイル
- Request、フォームデータ
- FlaskにおけるGET / POST
- Redirect、Session
- 環境変数、設定値と秘密情報
- Webアプリの基本テスト
- HTTP 200等をテストで確認する意味
- 最後にBOSS

### 08 データベース・SQL基礎訓練

- データベースとは、RDB
- Table、Row、Column、データ型
- Primary Key、Foreign Key、テーブル間の関係
- SQL、SELECT、WHERE、INSERT、UPDATE、DELETE
- WebアプリとDB
- ユーザー入力をDBへ渡す際の安全性の考え方
- 最後にBOSS

### 09 Git・開発基礎訓練

- バージョン管理、Git、Repository
- Working Tree、Stage、Commit、Commit履歴
- Branchの考え方
- Remote Repository、GitHubの役割
- Push、Pull、`.gitignore`
- Dependency、`requirements.txt`、README
- 自動テスト、ログ
- 開発→テスト→コミットの基本サイクル
- 最後にBOSS

### 10 セキュリティ基礎訓練

- 情報セキュリティ、機密性、完全性、可用性
- Threat、Vulnerability、Risk
- Authentication、Authorization
- Password、Passwordを安全に扱う考え方
- Hash、Encryption、HashとEncryptionの違い
- Least Privilege、Patch / Update、Backup
- Secret、Environment Variable、Defense in Depth
- 最後にBOSS

### 11 Webセキュリティ基礎訓練

- Webアプリに脆弱性が生まれる理由
- ユーザー入力を信用しない原則、Input Validation
- 安全なDBアクセスの考え方
- Authenticationの実装ミス、Authorizationの実装ミス
- Cookieの安全性、Sessionの安全性
- 安全な出力処理
- CSRFの概念、CSRF対策の考え方
- Error Messageと情報漏えい、Secretの漏えい
- ログの重要性、Monitoring、Defense in Depth
- 最後にBOSS

### 12 監視・インシデント対応基礎訓練

- 正常な状態、異常とは何か
- Log、Application Log、Access Log、Error Log
- ログから読み取れる情報
- Monitoring、Alert、Incident
- 初動、状況確認、影響範囲確認
- 封じ込め、原因調査、復旧、再発防止
- 記録を残す重要性
- 最後にLearnフェーズのFINAL BOSS

## 3. 通常戦の出題方針

知識系訓練は主に4択問題とする。問題数は固定せず、理解に必要な量を用意する。軽い小単元は3〜5問、標準的な小単元は5問程度、重要・複雑な小単元は5〜8問程度を目安とする。

Python系訓練（02 Python基礎Ⅰ、05 Python基礎Ⅱ、07 Flask・Webアプリ基礎）はコード記述式とする。可能な範囲で意味的に正しい別解を許容する。コード判定の実装では安全性を優先し、入力された任意コードをWebアプリのプロセスで無制限に実行しない。

## 4. BOSSの出題方針

各訓練の最後に必ずBOSSを置く。BOSSは複数HP制とし、1問の正解だけでは撃破できない。

知識系BOSSは、正誤判断、用語記述、複数単元を組み合わせた応用問題を用いる。通常戦より一段深い理解を求める。

Python系BOSSはコードを提示し、まず正しいか間違っているかを判断させる。間違っている場合は正しいコードへ修正させる。Syntax Errorだけでなく、実行可能でも目的を満たしていないコードを含める。

12のFINAL BOSSは、監視・インシデント対応の訓練を締めくくるとともに、Learnフェーズの修了を示す。

## 5. 教材方針

各小単元では必要に応じて、何のために学ぶか、基礎概念、仕組み、具体例、図解、コード例、よくある誤解、重要ポイントを扱う。教材を無理に短くせず、正しい理解と定着を優先する。ただし冗長な水増しはしない。

独立した復習問題や前提確認テストは設けず、教材直後の通常戦と訓練末尾のBOSSで学んだ知識を使う。後続のBuildとAttack & Defendでも、Learnで得た知識を異なる場面で再利用する。

セキュリティを扱う教材と演習は、ゲーム内部の仮想システム、開発者自身のローカル環境、明示的な演習専用環境に限定する。実在する第三者システムへの無許可の攻撃・スキャン等は扱わず、原因・防御方法・修正も学ぶ。
