# Phase 2 Build 初期版

## できること

トップの「開発ラボへ」から利用する。Learnの修了は必須にしていない。
コード、プレビュー、開発ナビゲーターを同じ画面で表示する。
アプリ名・HTML・CSS・Python・JavaScript・SQL等を自分で編集し、SAVEで保存する。
RUNは未保存の変更を保存してからプレビューを更新する。別ファイルを選んでも編集中の内容は保持する。
RUNボタンは毎回 `GET /` から開始し、前回のプレビューのパスやPOSTデータを引き継がない。
HTML/CSSモードでは選択中のHTML（その他のファイルを編集中なら `templates/index.html`）を表示する。
パス欄は直近のリクエスト先を表示する読取専用欄。別のRouteにはプレビュー内のリンク・フォームから移動する。
SAVEだけではプレビューを移動・再実行しない。RUNでもSession・DB・プロジェクト・チャットは初期化しない。
新規プロジェクトと新規ファイルを作成できる。初期版は1ブラウザーにつき10プロジェクト、
1プロジェクト30ファイル・合計500KB、1ファイル100KBまで。

最初は見出しや色を変更してRUNする。付属のapp.pyには、FlaskのRoute、フォーム入力、
パラメーター化したSQLite操作、Session、ログを使う小さな出発点を用意している。
用途を固定する課題や自動採点はなく、コードを書き換えて自分のテーマへ変更できる。

## 初回のAI COREガイド

Build初回アクセス → 作りたいものを自由入力 → 目的・主要機能候補・関連Learn・最初の実装を確認・編集
→ 「この内容でBuildを始める」で通常の3領域へ進む。選択式のアプリテンプレートや完成コード生成は行わない。
各項目は自由に修正・削除できる提案で、全部を初日に実装する必要はない。
入力は1〜1500文字、編集後の各項目は0〜1500文字。確認した提案はAIパネルの「はじめのアイデア」に残る。
案内途中でも「スキップして開発を始める」で終了できる。Escapeもスキップとして扱う。

初回の単位は署名付きCookie内の既存`build_owner`。`build.sqlite3`に`build_onboarding`テーブルを追加し、
所有者ごとの`completed`と確認済み`plan`（4文字列のJSON）を保存する。チャットやプロジェクトには混ぜない。
最初のプロジェクト作成前に未完了を記録し、完了・スキップ後は別プロジェクト作成時や再起動後も表示しない。
途中で閉じた場合は次回も案内を表示する（未確定入力は未保存）。完了保存に失敗した場合は内容を残して再操作できる。
Cookie削除・失効で所有者の対応を失った場合は、既存Buildと同様に別利用者になる。

既存所有者の初回判定では、その所有者のプロジェクトが既に存在し、案内レコードがなければ案内済みとして記録する。
テーブル追加と案内レコードの作成だけを行い、既存`projects`のコード・実行DB・Session・チャット・鍵・更新時刻を変更しない。
完了処理は未完了レコードにだけ適用するため、別タブの遅れたスキップで確認済みの案を上書きしない。

標準はローカル整理。入力の目的をそのまま保持し、記録・保存・入力などのキーワードがあるときだけ
フォーム・保存・一覧の候補とLearn第4・7・8訓練を追加する。その他のアイデアにはHTML/CSSの表示から案内する。
自由文の意味を完全に理解するものではないことを表示する。最初は既存HTMLの見出しを変えてSAVE/RUNする小さな作業。
Sessionやログは後から必要に応じて広げる方向だけを示し、Phase 3は実装しない。

OpenAI設定時は明示的な整理操作で既存`ask_guide`とproviderを使用する。初回整理のcontextは
`task=onboarding`、マスク済み入力・プロジェクト名・ファイル名・Learn索引のみで、コード本文・履歴・ログは送らない。
既存の秘密除去・送信サイズ上限・SDK30秒timeout・retryなしを継承する。返答は4文字列のJSONとして検証し、
通信失敗・空応答・形式不正・上限超過は既存のfallbackでローカルへ戻す。実API接続は今回のテストでは行わない。
ブラウザーは整理40秒・完了保存15秒で待機を終了し、入力を維持する。整理中もスキップでき、遅延応答で案内を再表示しない。
表示にはtextarea.value / textContent、初期データにはJinjaのtojsonを使用し、自由入力やAI出力をHTMLとして解釈しない。
APIは既存のCSRF・Origin・所有者境界を利用し、確認後の案も秘密除去して保存する。

## 実行できる範囲を区別する

### 標準のHTML/CSSモード

追加インストールなしで、保存したHTMLとCSSをブラウザーで描画する。
Python、Jinja、SQL、利用者のJavaScriptは実行しない。Jinjaの記法はそのまま表示される。
フォームの見た目は確認できるが、送信するとFlaskモードが必要であることを表示する。
サーバーでの保存を行ったように見せる模擬処理はしない。

HTMLは許可したタグと属性だけで再構築し、画像・外部リンク・埋め込み・スクリプトを取り除く。
CSSは同じプロジェクト内のファイルだけを埋め込む。ネットワーク先のCSSや画像を取得しない。
JavaScriptのファイルも編集・保存できるが、初期版では実行しない。
任意JSを実行できるiframeは自分自身の外部URLへの移動などが可能なため、
ネットワーク遮断をCSPだけに任せる設計にはしていない。

### 任意設定のFlaskモード

Linuxコンテナー対応のDockerが利用でき、専用イメージを作成した場合だけ有効。
初期実装時はDocker未導入だったが、現在は下記のRUN回帰確認を実コンテナーでも実施済み。
ホストで利用者のPythonを直接実行する代替処理はない。

Docker Desktop等を利用者自身で用意した後、リポジトリのルートで実行する。
イメージ作成時だけPythonイメージとFlaskの取得に通信が必要。実行時の外部通信は無効。

```powershell
docker build -t cyber-build-runtime:1 ./build_runtime
$env:BUILD_DOCKER_ENABLED = "1"
python -m src.app
```

ブラウザー側RUN操作の回帰テストはNode.jsの標準機能を使用するため、全pytest実行には
`node` がPATH上に必要（npmパッケージの追加は不要）。

Buildの実行モードで「Flask」を選びRUNする。`app.py`の`app`をFlaskアプリとして読み込み、
Flaskのテストクライアントで実際のRequest / Responseを処理する。
プレビュー内のフォームやローカルリンクは、固定の橋渡しコードからBuildへ依頼し、
新しい隔離コンテナー内で次のリクエストを処理する。公開ポートやWebサーバーの常駐は不要。
リダイレクトはローカルパスのみ、最大5回。GETとPOSTに対応する。

各リクエストでプロセスは作り直すため、Pythonのグローバル変数は永続状態には使えない。
継続したい値はSessionまたはDBを利用する。
DBは`data/app.sqlite3`の1ファイル、1MBまで。Session Cookieはプロジェクト専用の状態として保存し、
LearnのCookieと混ぜない。標準ライブラリとFlask以外のパッケージ追加や任意pip installは未対応。
Flaskモードでも利用者のJavaScriptや外部リソースをプレビューへ渡さない。

## 実行境界と制限

- ゲーム本体はコードを保存するだけ。`exec`、`eval`、ホストでの利用者コードimportはしない。
- コンテナーへホストのフォルダ、Dockerソケット、本体secret、Learnデータをマウントしない。
- Docker接続先はローカルのnamed pipe / Unix socketに限定し、SSHやTCPの外部デーモンを使用しない。
- コードとそのプロジェクトの状態だけを標準入力で渡す。
- ネットワークなし、公開ポートなし、非rootユーザー、権限削除、昇格禁止、ルート領域は読取専用。
- 書込先は容量制限付きtmpfs。メモリ192MB、CPU 0.5、プロセス32、実行時間10秒、出力3MB。
- 終了・時間超過・出力超過の後は対象コンテナーを削除する。
- 返却されたDBはサイズと形式を検証して保存し、ゲーム本体のSQLiteとして開かない。
- プレビューiframeは別のopaque originで動作し、同一オリジン、トップ移動、ポップアップ等を許可しない。
- 許可リストでHTMLを再構築し、CSPで外部通信・画像・埋め込み・フォームの直接送信を遮断する。
- sandboxのallow-formsはsubmitイベントを受け取るために使用する。実際の送信は固定スクリプトで取り消し、CSPのform-actionでも禁止する。
- プレビューの固定スクリプトだけをランダムなnonceで許可する。親は送信元ウィンドウとトークンを確認する。
- 保存・実行APIには所有者照合、CSRFトークン、Origin確認、サイズ制限を設ける。

Dockerは完全無欠な安全境界ではない。OS・Dockerの更新と、リソース制限が機能するLinux環境が必要。
この初期版は本人のローカル開発用であり、不特定多数の敵対的コードを受け入れる公開サービスではない。
ホストOS上の別プロセスによるファイル改変、Dockerデーモン管理者、ブラウザーやカーネルの脆弱性までは防がない。
長大なCSS等による表示の重さも完全には排除できない。停止できないプレビューはページを再読み込みする。

## 保存とPhase 3への接続

`instance/build.sqlite3`に、プロジェクトID、所有者、ファイル一覧と本文、作業ファイル、保存バージョン、
実行用DB、アプリSession、チャット履歴を保存する。ユーザーの入力パスをホストの保存パスとして使わない。
ファイル更新はバージョンが一致した場合のみ受け付け、別タブによる上書きを検出する。
プロジェクト専用の秘密鍵はサーバー側で生成・保存し、ソースコードや編集APIには含めない。

所有者IDは既存の署名付きCookieのBuild専用キーに保存する。ゲーム再起動後も同じブラウザーと
同じ署名鍵で再開できる。Learnの約90日のCookie保持設定を利用する。
Cookieを消すと、そのブラウザーとプロジェクトの対応を失う。アカウントや復元UIは今回用意しない。
バックアップする場合は、アプリを停止して`instance`フォルダ全体を保管する。Gitへ登録しない。

将来のPhase 3はこのプロジェクトIDと保存データを利用し、修正は同じBuildへ戻す。
コード、DB、Sessionを継続して持てる境界は用意したが、Phase 3本体・攻防機能は未実装。

## 開発ナビゲーター

AI COREは仮ラベルで、`BUILD_AI_LABEL`設定で変更できる。CSSの同心円・細線・青緑の光を使った
独自の表示であり、参考画像の名称・ロゴ・配置・画像データを使用していない。

標準動作は**生成AI未接続のローカルガイド**。現在のファイル、質問のキーワード、一部コードを基に、
考え方、確認箇所、短い例、対応するLearn訓練を案内する。自由な自然文を理解するLLMではないため、
未対応の質問には一般的な案内を返す。利用者のコードを自動で書き換えない。
チャットは最大20メッセージをプロジェクトへ保存し、再読み込み後も表示する。

### OpenAI接続

`OPENAI_API_KEY`環境変数があれば、`src/build_openai.py`の`OpenAIGuide`を起動時に登録する。
公式Python SDK `openai>=2.54,<3`（確認バージョン2.54.0）の`client.responses.create`を使う。
既定モデルは`gpt-5.6-terra`。公式にResponses対応・知能とコストのバランス型とされるため採用した。
`BUILD_AI_MODEL`で変更可能。GPT-5/6系には`reasoning.effort=low`を指定し、対話の待ち時間を抑える。
別モデルへの変更時は、そのモデルのResponses対応と利用権限を確認する。

設定例はREADMEのPowerShell手順を参照。`.env`読込やキー入力Webフォームは追加していない。
実キーは環境変数から読み、サーバープロセス内だけで利用する。キー未設定なら通信せずローカルガイド。
送信先は`https://api.openai.com/v1`に固定し、`OPENAI_BASE_URL`や環境プロキシは利用しない。
API障害時もLearn、保存、プレビューには依存させない。

### 送信内容と制限

送信は明示的なチャット質問時、または初回ガイドの整理操作時だけ。「次の一歩」・ファイル切替・SAVE・RUNはAPIを呼ばない。
入力は固定の役割指示と、解析対象データを分ける。コードやログ内の命令を上位指示へ昇格させない。

| 情報 | 上限・選択方法 |
| --- | --- |
| プロジェクト名 | 80文字 |
| ファイル名 | 最大30件、各120文字。全ファイル本文は送らない |
| 現在のファイル | ファイル名120文字、コード先頭6000文字。省略フラグ付き |
| 実行情報 | 現在のモード、直近RUNのモード・HTTP status・保存revision、ログ末尾2000文字 |
| 質問 | 1500文字 |
| 会話 | 直近6メッセージ、各800文字。保存は引き続き20メッセージ |
| Learn | 正式12訓練とUNIT見出しの索引、最大2800文字。教材本文・問題・進捗は送らない |
| データ全体 | JSON化後24000文字を超えたら送信せずローカルガイド |
| 出力 | 最大2400トークン（推論分を含む）、表示・保存は最大6000文字 |

実行ログはブラウザーが直近結果を保持し、質問と同時に送る。DBには追加保存しない。
コード修正後に未RUNの場合もあるため、現在の保存revisionと実行時revisionを分け、申告データと明記する。
再読み込み直後はそのページでの最新RUN結果を使う。古いタブのログや改変された申告を検証済み事実とは扱わない。

OpenAIの応答保存は`store=False`。これはサービス全体のログ保持をゼロにする設定ではない。
生成AIの出力は検証済みコードではなく提案。本人が確認し、エディタへ反映してRUNする。

### 機密情報とエラー処理

`build_ai_context.py`で送信項目を許可リスト化する。実行用DB、Cookie、内部鍵、CSRFは項目に含めない。
既知のAPIキー・Flask鍵・Build内部鍵・Session値・CSRFと、明白なキー代入・Bearer・秘密鍵を
コード、ログ、質問、履歴からマスクする。回答とチャット保存にも同じマスクを適用する。
元の編集コードは書き換えないため、利用者自身が秘密をコードへ書けば従来どおり保存対象になる。
マスクは完全な秘密検出ではない。個人情報や独自形式の秘密も入力しないこと。

SDKの通信timeoutは30秒、自動retryは0回。ブラウザーは40秒で待機を終了し、操作と質問文を戻す。
通信timeoutはSDKの通信待ち制限であり、厳密な全処理時間の保証ではない。
ブラウザー側の待機終了後にサーバーの回答保存が完了する場合は、再読み込みして履歴を確認する。
認証・利用上限・モデル設定・通信失敗・timeout・不完全/空の応答は短い案内付きでローカルへ戻る。
SDK例外本文を画面へ返さず、サーバーログには失敗分類だけを記録する。会話・コード・鍵はログ出力しない。

Dockerのネットワーク遮断・マウント禁止・実行制限は変更していない。SDKはゲーム本体側だけで使用し、
コンテナーのイメージには追加しない。APIキーをDockerの引数・標準入力・コンテナー環境へ渡さない。

### provider境界と表示

既存どおり`application.config["BUILD_AI_PROVIDER"]`へ以下のオブジェクトを渡して差し替えられる。

```python
class GuideProvider:
    mode = "利用するAIサービスの表示名"

    def reply(self, context, history, question):
        # context: 上記許可項目だけの辞書。秘密除去・サイズ制限済み。
        # history: 直近6メッセージ、各800文字。戻り値は回答の文字列。
        # APIキーは環境変数等から読み、ソースコードへ記述しない。
        # 通信時間制限を設け、失敗時は例外を返す。
        ...
```

UIは3領域と円形COREを維持。PROCESSING・送信中・成功・fallback・通信失敗を表示する。
送信中は二重送信を防ぎ、終了時に操作を戻す。回答HTMLは解釈しない。
コードフェンスだけ`pre/code`に分け、本文もコードも`textContent`で描画する。一般MarkdownのHTML化は行わない。

役割指示は、考え方→現在のコードで見る場所→次の操作→必要なら例の順に初心者を支援する。
コードを求められたら具体的に支援し、見ていないファイルや実行結果を断言しない。
ツール、自動編集、自動RUN、外部検索、Phase 3や自律エージェントは実装していない。

### 少数回の実API確認

キーを設定して再起動後、秘密を含まないサンプルプロジェクトで「フォームをFlaskで受け取りたい」と
1回質問する。表示が`OpenAI 生成AI`となり、コードと関連する説明が返ることを確認する。
必要なら、RUNで得たエラーについてもう1回だけ質問する。エラーの原因候補を参照できることを確認する。
認証エラー時は権限とキー、モデルエラー時は`BUILD_AI_MODEL`を確認する。キーそのものはログに出さない。
設定解除後はローカルガイドになる。通常pytestはSDKのHTTPをmock化し、実APIを呼ばない。

参照した公式資料：
[Responses API](https://developers.openai.com/api/reference/python/resources/responses/methods/create)、
[公式SDK](https://developers.openai.com/api/docs/libraries)、
[GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)、
[テキスト生成と指示](https://developers.openai.com/api/docs/guides/text)。

## 開発者向け構成と確認

| ファイル | 役割 |
| --- | --- |
| `src/build_routes.py` | Buildの画面とAPI、所有者・CSRF確認 |
| `src/build_store.py` | ファイル検証、SQLiteへの保存、更新競合確認 |
| `src/build_starter.py` | 編集可能な出発点 |
| `src/build_runtime.py` | Docker呼び出しと出力制限。ホストPython実行はしない |
| `build_runtime/runner.py` | コンテナー内のFlaskリクエスト処理 |
| `build_runtime/Dockerfile` | PythonとFlaskの専用イメージ |
| `src/build_preview.py` | HTML再構築、CSP、フォーム・リンクの橋渡し |
| `src/build_ai.py` | ガイドの差し替え境界とローカルガイド |
| `src/build_openai.py` | 公式SDKのResponses API、役割指示、通信制限・エラー分類 |
| `src/build_ai_context.py` | 送信項目・文字数の制限、秘密除去、Learn索引 |
| `src/build_onboarding.py` | 初回ガイドの4項目・ローカル提案・返答検証 |
| `src/templates/_build_onboarding.html` / `src/static/build_onboarding.js` | 初回モーダル、自由入力・編集・スキップ・提案の表示 |
| `tests/test_build_onboarding.py` / `tests/build_onboarding_checks.cjs` | 初回判定、移行、永続化、SDK mock、UIイベント・安全な描画 |
| `src/templates/build.html` / `src/static/build.*` | 3領域UI、textareaエディタ、保存・実行操作 |
| `tests/test_build.py` | 保存、復元、隔離境界、プレビュー、ガイドの検証 |
| `tests/test_build_ai.py` | 実通信しないSDKテスト、送信内容・fallback・保存の検証 |
| `tests/build_run_checks.cjs` | 実際のJSによるRUN・チャットのイベント処理、安全な描画 |
| `src/app.py`（変更） | Build Blueprintと設定の登録 |
| `src/templates/index.html`（変更） | Buildへの入口。Attack & Defendは準備中 |
| `tests/test_boss_replay.py`（変更） | トップの準備中表示が2個から1個になる期待値を更新 |
| `README.md`（変更） / `docs/BUILD.md`（新規） | 利用手順、実行条件、制約、設計・検証結果 |

```powershell
python -m pytest
python -m src.app
```

ブラウザーでトップ→Build→HTML編集→SAVE→RUN→CSSへ切替→編集→RUN→質問→再読み込みを確認する。
Dockerを設定した環境では、Flaskへ切り替えてフォーム送信、DB保存、Session、ログを確認する。
構文エラー、無限ループ、外部通信、ホストのファイル参照が本体に影響せず終了することも確認する。
自動テストの実行境界テストはテスト用ランナーを用い、ホストで利用者のPythonを実行しない。

初期版実装時の確認結果：全208 pytest成功（既存165件とBuildの43件）。
`node --check src/static/build.js`、`git diff --check`も成功。
実ブラウザーの1280×720で3領域を同時表示し、HTML/CSS編集、保存、RUN、ファイル追加・切替、
チャット、プロジェクト追加・切替、再読み込み、アプリ再起動後の復元を確認した。
未設定のFlask処理を要求した場合は説明を表示する。

RUNのURL初期化修正時の確認結果：全214 pytest成功（既存208件＋回帰6件）。
`tests/build_run_checks.cjs`で実際の`build.js`を読み込み、RUN・保存・iframeメッセージの
イベント処理を検証する。固定FlaskテストアプリではGETリンク、POST→Redirect、Session・DB・保存状態の継続も確認する。
`node --check src/static/build.js`、`node --check tests/build_run_checks.cjs`、`git diff --check`も成功。
本体とは別の検証用保存領域と実Dockerを使い、ブラウザーでPOST専用`/count`→RUN→`GET /`、
旧ルートのない別アプリへの変更→RUN、GETリンク、POST→Redirect、SAVEのみで表示維持、HTML/CSSを確認した。
再RUN・コード変更後もSession値3とSQLiteの3行が残ることを確認した。
最初のDocker実行は既存の10秒制限に達したが、再実行以降は成功。隔離・実行制限は変更していない。

生成AI接続追加時の確認結果：全241 pytest成功（既存214件＋AI関連27件）。
SDK通信をMockTransportへ置換し、成功、認証、利用上限、不正モデル、timeout、接続失敗、応答異常、
秘密除去、context上限、履歴、安全な表示、二重送信防止、DockerへAPIキーを渡さないことを検証した。
実ブラウザーの1280×720で3領域を維持し、未設定時のローカル回答、模擬APIの待機・成功・fallback、
コード例の表示、HTML文字列が要素にならないこと、履歴再読込を確認した。
実際の認証付きOpenAI API呼び出しは、作業環境のAPIキー未設定により未実施。

初回オンボーディング追加時の確認結果：全270 pytest成功（既存241件＋29件）。
初回判定・未完了/完了/スキップの再起動保持・複数プロジェクト・所有者境界・既存データ移行・
自由入力上限・HTMLエスケープ・秘密除去・SDK mock成功・fallback・提案の編集・入力へ戻る・
送信失敗・整理中のスキップ・遅延応答を検証した。通常チャットと初回整理の役割指示は分離した。
`node --check`（build.js / build_onboarding.js / build_onboarding_checks.cjs）、`git diff --check`も成功。
実ブラウザーの1280×720で初回入力→4項目の確認・編集→開始→再読み込みで再表示なし、
通常チャット・SAVE・RUN・HTML/CSSプレビューを確認した。ブラウザー検証は別の保存領域を使用した。
既存の実データ（1プロジェクト・1所有者）は読み取り専用で複製し、複製への移行後に
全プロジェクト列のハッシュが一致することを確認。元の保存コード・実行DB・Session・チャットは変更していない。
有料API通信と実Dockerの再実機テストは今回行っていない。Dockerの実装は変更せず既存の回帰テストで確認した。

隔離方式の確認に参照した一次資料：
[Dockerの実行制限](https://docs.docker.com/engine/containers/run/)、
[Dockerのセキュリティ](https://docs.docker.com/engine/security/)、
[MDN iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)、
[MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)。
