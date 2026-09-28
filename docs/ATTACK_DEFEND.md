# Phase 3 — Attack & Defend 初期版

## 起動と構造

Learnの知識を、Buildと共通のDocker隔離環境で実践する。初期MVPの概念的な攻防案に対して、
現在の実装仕様は本書を優先する。Learn・Buildの進捗や教材、保存データは変更しない。

[BUILD.md](BUILD.md) に従って `cyber-build-runtime:1` を作成し、Docker DesktopのLinuxコンテナーを起動する。

```powershell
$env:BUILD_DOCKER_ENABLED = "1"
python -m src.app
```

トップの「攻防演習へ」で `/arena/` を開く。未設定時は画面だけ表示し、実行は理由を示して停止する。
Docker準備は段階ごとに最大30秒待ち、runnerのREADY通知後にコード実行の10秒上限を開始する。
旧イメージを使っている場合は [BUILD.md](BUILD.md) の手順で一度再ビルドする。
実行失敗で要求回数・攻略状態は進まない。OpenAI API・外部検索・AIによるターゲット生成は使用しない。

| ファイル | 役割 |
| --- | --- |
| `arena_scenarios.py` | シナリオ辞書、難易度、ヒント、関連Learn |
| `arena_targets.py` | Docker内だけで動かす架空Flaskアプリ |
| `arena_engine.py` | 抽選、進行、成否、コピー、入口制御、時間管理 |
| `arena_store.py` | Phase 3専用SQLite保存 |
| `arena_routes.py` | 所有者・CSRF・操作・実行境界 |
| `arena.html` / `arena.css` / `arena.js` | 共通HUD、HTTP操作、ログ、Local Guide |

## Attack

常時3候補 → 選択 → GET / の案内を読む → パス・メソッド・入力を操作 → 応答とログを観察 →
成功／要求上限／手動終了 → 振り返り → 選択した枠だけ補充、という流れ。

入力は文字列の値を持つJSON。GETはクエリ、POSTはフォームとして扱う。
Docker内のFlask test clientから実際に対象アプリへ渡す。応答HTMLもプレーンテキスト表示する。
成功はHTTP 200の応答に、その挑戦専用の非公開演習マーカーが含まれた場合だけ。
挑戦IDと要求番号で重複送信を拒否する。選択画面に脆弱性・マーカー・攻略法は渡さない。

### 初期シナリオ

3候補と直後の再登場防止を両立するため、各難易度4件、計12定義とした。
以下の4テーマを難易度別に共有する。異なる12種類の脆弱性を用意したわけではない。

| 架空サービス | 原因 | 関連Learn |
| --- | --- | --- |
| Lumen Archive（記録） | オブジェクト単位の認可不足 | 4・7・11 |
| Nacre Reports（帳票） | GETとPOSTの認可不整合 | 4・7・11 |
| Vela Catalog（検索） | 入力文字列を連結したSQL | 8・11 |
| Orin Monitor（稼働情報） | 診断情報のアクセス制御不足 | 4・10・11・12 |

同じ難易度内で3候補は重複せず、補充時には残り2候補と直前に終了したシナリオを除外する。
上限はEasy 14要求、Normal 10要求、Hard 12要求。Hardは接続セッション確立→カタログ確認→
対象操作という複数段階が必要で、記録番号も変わる。応答や403を読み次の操作を判断する。

## Defend

保存済みBuildプロジェクト・テーマ・パスを選択 → 隔離コピー → 開始 → 通信ログを観察 →
入口ルールを編集 → 次の通信で検証 → 成否と振り返り → 必要ならBuildへ戻り自分で改善する。

`app.py` があり、指定パスへの通常GETが成功するプロジェクトが必要。
テーマは「不審な取得要求」と「過大入力」の2種類。1波につき通常閲覧2要求と不審要求2要求を処理する。
遮断されなければ不審要求もDocker内のコピーへ実際に届き、DBやSessionが変化する場合がある。
大量負荷攻撃ではない。送信元は演習用ラベルであり、実在IPではない。

```json
{"blocked_sources": [], "max_body": 10000}
```

- `blocked_sources`: ログから選んだ送信元ラベルを入口で403拒否する（10件まで）。
- `max_body`: フォームの値をUTF-8にした合計バイト数の上限。超過は413で拒否する（0〜10000）。
  ヘッダー等を含む汎用Webサーバーのサイズ上限ではない。

2つの不審要求を拒否し、かつ2つの通常GETを成功させた場合だけ防御成功。
入口での拒否のほか、アプリ側の400・401・403・405・413・422・429も拒否と扱う。
404・500は防御成功にならず、全員を遮断して通常閲覧を失う設定も失敗になる。
成功はこの要求列に対する検証であり、アプリ全体の安全性・全機能の正常動作を保証しない。

入口ルールは演習専用。コードの自動修正・Buildへの自動適用はしない。
振り返りではログ・入力検証・認可・監視を見直す考え方と関連Learnを示す。
Buildへのリンクは元のプロジェクトを選択する。自分で変更・保存した後は新しいコピーで演習できる。

## 難易度とLocal Guide

- **Easy（初期値）**: 2段階のヒントと関連Learn。Local Guideのみで利用できる。
- **Normal**: 挑戦中のヒントなし。終了後の原因・改善点・関連Learnは表示する。
- **Hard**: Attackは複数段階。Defendは開始ボタンなしで表示中に不定時の攻撃が起こる。

難易度バーは上部に固定。変更時は進行中の挑戦・コピー・候補を作り直すがLearnとBuildは変更しない。
Hard選択時は最新Buildプロジェクトに `app.py` があれば自動でコピーして監視を開始する。
別の対象はDefendでコピーし直せる。対象がない場合は準備を案内する。

### Hardの時間管理

本番は20〜45秒のランダムな「Phase 3表示時間」を待機時間とする。3秒ごとの通知で進める。
Attackを表示中でも事件を上部に通知する。事件中・結果後は重ねて発生せず、新しいコピーで再開する。

- 非表示・ページ離脱でタイマー停止。復帰時は基準時刻をリセットする。
- 再読み込みでも残り時間・コピー・事件を保持し、閉じていた時間を加算しない。
- 8秒超の通知間隔は通信途絶と扱い、遅れた通知による一斉発火を防ぐ。
- 最新ページの識別子だけが時計を進める。古いタブは進められない。
- タイマーは1本。離脱前に受理した有限の実行は完了する場合がある。
- OS常駐処理、バックグラウンドジョブ、常駐コンテナーはない。

テストには `ARENA_HARD_DELAY`、`ARENA_CLOCK`、`ARENA_RANDOM` を設定注入できる。
偽ランナー `ARENA_RUNTIME` は `TESTING` の場合だけ利用可能で、本番はDocker限定。

## 永続化とBuild保護

`instance/arena.sqlite3` に、所有者ごとの候補・進行中の挑戦・コピー・直近10件の結果を保存する。
既存の約90日sessionとBuild所有者IDを利用する。別の所有者のBuildプロジェクトは参照できない。
SQLiteトランザクションとBuild共通の実行ロックで操作を直列化する。

BuildStoreは読み取りだけ。Defendは `files`、`runtime_state`（DBとSession cookie）、
`runtime_secret` をdeep copyする。元ID・名前・保存revisionは出典として保持する。
コピーのSessionを維持するため使うのはアプリ専用鍵で、ゲーム本体のFlask鍵ではない。
チャット・オンボーディング・他プロジェクトはコピーせず、Buildへ一切書き戻さない。
ブラウザーには公開データだけを返し、内部ソース・cookie・秘密値は返さない。

## sandboxと安全境界

既存 `DockerRuntime` を再利用し、本体Flask内で対象コードを実行する経路は追加しない。

- ローカルnpipe/unix endpointのみ。remote Docker daemonを拒否。
- `--network none`、ポート公開なし、ホストvolume・Docker socketのマウントなし。
- 非root、読み取り専用root、capability全削除、no-new-privileges。
- メモリ192MB、CPU 0.5、PID 32、1実行10秒、tmpfs容量制限。実行後はコンテナーを削除。
- 承認されたプロジェクトファイルとコピーのDB/Sessionだけを標準入力で渡す。
- ホスト環境変数・OpenAIキー・Learnデータ・`.git`・他プロジェクトは渡さない。
- HTTPはコンテナー内のtest clientのみ。外部URL・IP・LANに向けた通信UIはない。
- 既存の応答量・保存データ量制限、秘密除去、画面のtextContent描画を維持する。

既存Build同様、ローカル演習の隔離境界であり、敵対的な第三者コードを公開サービスとして受け入れる設計ではない。

## シナリオを追加する方法

Attackの共通辞書には以下を持たせる。

```text
id / difficulty / title / target_type / description / objective / family
initial_state / vulnerability / success_condition / failure_condition
request_limit / easy_hints / related_learn / post_failure_advice
```

1. `SCENARIOS`に同形式の定義を追加。同一難易度は最低4件を維持する。
2. 既存familyならデータ追加。新しい実挙動が必要なら `arena_targets.py` にfamilyを追加し、
   非公開データへ挑戦専用markerを置く。共通HTTP・marker方式ならroutes・HTML・JS・DB schemaは変更不要。
3. 公開説明は攻略法を漏らさず、段階ヒント・終了後の防御方法・関連Learn番号を記載する。
4. 実Dockerテストに正常操作と攻略手順を追加する。

初期判定方式は `response_marker` と `request_limit_or_finish` のみ。
定義文字列の変更だけで新しい判定方式が自動生成されるわけではない。
Defendは `DEFEND_SCENARIOS` にmethod/data・説明・ヒント・助言を追加する。
別の通信列や成否条件を導入するときだけengineのイベント生成・判定を拡張する。

## 検証

```powershell
python -m pytest -q
node --check src/static/arena.js
node --check tests/arena_checks.cjs
git diff --check

# 実Dockerを明示的に有効化
$env:ARENA_DOCKER_TESTS = "1"
python -m pytest tests/test_arena.py -k actual_docker -q
Remove-Item Env:ARENA_DOCKER_TESTS
```

通常pytestは固定応答ランナーで進行・所有者境界・コピー保護・タイマー・UIイベントを確認し、
実Docker検証はskipする。固定ランナーは対象ソースを本体で実行しない。
ブラウザー確認は別の検証用保存先を使い、Attackの攻略と補充、Defendのログ・対処・通常閲覧を確認する。
Build全列のダイジェスト比較で、元コード・DB・Session・チャットが変わらないことも検証する。

### 初期実装時の確認結果（timeout分離前・2026-09-28）

- 通常実行：305件成功、明示的な実Dockerテスト12件はskip。
- 実Dockerを含む直近の全実行：316件成功、1件失敗。
  `easy-records` のDocker接続確認・起動で失敗し、個別再実行では既存の10秒上限に達した。
  同シナリオは先行する個別実行と実ブラウザーで成功しているが、実機試験が常時安定して成功する状態とは報告しない。
  Dockerの利用可否や起動待ちの影響は残っており、隔離・実行時間制限を緩める変更は行っていない。
- JavaScript構文確認と `git diff --check` は成功。
- ブラウザー：記録サービスの攻略→対象1件補充、過大入力への対処→413拒否＋正規GET 200→防御成功、
  Hardの開始ボタンなしの事件発生、再読み込み後の事件保持を確認。
- 検証用Build全列のダイジェストは攻防演習前後で一致。本来の利用者データは検証に使用していない。

90シナリオ、外部接続、攻撃エージェント、自動修正、報酬・XP等は今回実装しない。

### timeoutの責務分離

`easy-records` の追加調査で、cold startのdaemon確認が3.215秒かかり、旧3秒上限では
利用可能なDockerを利用不可と判定する問題を確認した。過去の10秒超過時の段階ログは残っておらず、
その回の停止箇所は断定できない。今回のシナリオ読込・HTTP処理は合わせて約0.09秒だった。

現在はDockerの準備待ちと未信頼コード実行を分離する。create/start後、信頼済みrunnerのREADY通知を
確認して初めてコードを送る。その時点からホストで10秒を計り、コンテナー内の監視役も独立して10秒で停止する。
詳細は [BUILD.md](BUILD.md#docker準備とコード実行の時間制限) を参照する。
runtimeの自動再試行は追加していない。シナリオ・成功条件・難易度・UI・保存仕様も変更していない。

修正後のDocker Desktop再起動直後の計測：

| 段階 | 秒 |
| --- | ---: |
| daemon確認 | 2.424 |
| image確認 | 0.865 |
| container create | 0.464 |
| startからrunner READY | 1.358 |
| 入力転送・コード実行・結果回収 | 0.387 |
| cleanup | 0.220 |

warmの3回連続実行ではREADY後の処理は約0.26〜0.28秒。
無限ループは読み込み時・HTTP処理中とも約10秒で停止し、コンテナー削除も確認した。
準備に12秒かかる状況は模擬時計で検証し、実行予算を消費しないことを確認している。

最終確認：`ARENA_DOCKER_TESTS=1` で全330件成功（通常回帰312件＋実Docker18件、142.67秒）。
実Docker18件は既存シナリオ12件、easy-records反復3件、無限ループ2件、監視役の独立停止1件。
既存assertionを削除・緩和せず、create/start分離に合わせて安全境界テストのモックを更新した。
`node --check`（arena.js、build.js、arena_checks.cjs）と `git diff --check` も成功。
