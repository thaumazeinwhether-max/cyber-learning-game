# Phase 2 Build 初期版

## できること

トップの「開発ラボへ」から利用する。Learnの修了は必須にしていない。
コード、プレビュー、開発ナビゲーターを同じ画面で表示する。
アプリ名・HTML・CSS・Python・JavaScript・SQL等を自分で編集し、SAVEで保存する。
RUNは未保存の変更を保存してからプレビューを更新する。別ファイルを選んでも編集中の内容は保持する。
新規プロジェクトと新規ファイルを作成できる。初期版は1ブラウザーにつき10プロジェクト、
1プロジェクト30ファイル・合計500KB、1ファイル100KBまで。

最初は見出しや色を変更してRUNする。付属のapp.pyには、FlaskのRoute、フォーム入力、
パラメーター化したSQLite操作、Session、ログを使う小さな出発点を用意している。
用途を固定する課題や自動採点はなく、コードを書き換えて自分のテーマへ変更できる。

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
この開発環境にはDockerが存在しなかったため、**実コンテナーでの実行確認は未実施**。
ホストで利用者のPythonを直接実行する代替処理はない。

Docker Desktop等を利用者自身で用意した後、リポジトリのルートで実行する。
イメージ作成時だけPythonイメージとFlaskの取得に通信が必要。実行時の外部通信は無効。

```powershell
docker build -t cyber-build-runtime:1 ./build_runtime
$env:BUILD_DOCKER_ENABLED = "1"
python -m src.app
```

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

生成AIの認証情報は未設定。鍵を仮作成せず、外部API通信も実装していない。
今後は`application.config["BUILD_AI_PROVIDER"]`へ、以下を持つオブジェクトを渡して差し替えられる。

```python
class GuideProvider:
    mode = "利用するAIサービスの表示名"

    def reply(self, context, history, question):
        # context: project_name, active_file, code（最大6000文字）
        # history: 直近10メッセージ。戻り値は回答の文字列。
        # APIキーは環境変数等から読み、ソースコードへ記述しない。
        # 通信時間制限を設け、失敗時は例外を返す。
        ...
```

接続失敗時はローカルガイドへ戻る。将来外部プロバイダーを実装する際は、
コードが外部へ送られることの表示、タイムアウト、費用と送信範囲の管理が別途必要。

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
| `src/templates/build.html` / `src/static/build.*` | 3領域UI、textareaエディタ、保存・実行操作 |
| `tests/test_build.py` | 保存、復元、隔離境界、プレビュー、ガイドの検証 |
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
未設定のFlask処理を要求した場合は説明を表示する。実Docker実行と外部生成AI接続は未検証・未設定。

隔離方式の確認に参照した一次資料：
[Dockerの実行制限](https://docs.docker.com/engine/containers/run/)、
[Dockerのセキュリティ](https://docs.docker.com/engine/security/)、
[MDN iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)、
[MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)。
