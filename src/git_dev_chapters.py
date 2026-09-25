"""正式第9訓練の参考書型教材。コマンドは説明用で実行しない。"""

from src.chapter_blocks import code, flow, key_points, note, paragraph, section, table, warning


CHAPTERS = {
    "version_control": {
        "objective": "バージョン管理が変更の内容・時点・担当者を記録する理由を説明し、バックアップとの違いを述べられる。",
        "why": "第1〜8訓練で作るコードや教材を、変更の理由が分かる形で育てるためです。",
        "connection": "これまではアプリの動きとデータを学びました。今回は作ったものを安全に改善する開発の仕組みを学びます。",
        "sections": [
            section("変更を記録する",
                paragraph("バージョン管理は、ファイルがいつ・誰によって・どう変わったかを追えるようにする仕組みです。単に最新のファイルを残すだけでなく、変更前後の差と、その変更をひとまとまりにした記録を確認できます。間違いの原因を探すときも、どの変更で起きたかをたどる手がかりになります。"),
                flow("仕様を確認する", "コードを変更する", "差分を確認する", "変更理由とともに記録する", "後から履歴を読む"),
                table(["方法", "主な目的"], [["バックアップ", "障害・紛失に備えて別のコピーを保管"], ["バージョン管理", "変更の順序・内容・理由を追う"]])
            ),
            section("共同作業でも役立つ",
                paragraph("複数人で作業する場合、誰が何を変えたかを知ることは相談やレビューに役立ちます。一人で開発する場合も、昨日の変更理由を思い出す助けになります。ただし履歴があるだけでバックアップが万全になるわけではありません。別媒体や別場所への保管には別の対策が必要です。"),
                warning("「バージョン管理＝バックアップそのもの」と考えると、保存先の故障や秘密情報の漏えいへの対策を見落とします。"),
                note("確認例", "昨日は正常だった画面が今日壊れたとき、変更履歴と差分を見れば原因候補を絞れます。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "バージョン管理は変更の履歴を扱います。", "差分から何を変えたか分かります。",
                "変更理由も記録すると後で理解しやすくなります。", "共同作業でも個人作業でも役立ちます。",
                "バックアップと目的が重なる部分はありますが同じではありません。")),
        ],
    },
    "git_repo": {
        "objective": "GitとGitHubを区別し、repository・local repository・.gitの役割を説明できる。",
        "why": "このプロジェクトの履歴がどこに保存され、コマンドが何を見ているか知るためです。",
        "connection": "変更履歴が必要な理由を学びました。Gitはそれを実現する道具です。",
        "sections": [
            section("Gitとrepository",
                paragraph("Gitは分散型バージョン管理システムです。「分散型」は各開発者のPCに履歴を持つローカルrepositoryがあり、ネット接続がない状態でも多くの履歴操作ができる、という基本像です。repositoryは履歴とその管理情報を持つ場所です。通常、作業フォルダ内の.gitがGitの管理情報を保持します。"),
                code("git status", "現在の作業状態を見るコマンド。ローカルの作業フォルダで使います。", "powershell"),
                paragraph("git statusは変更済み・未追跡・stage済みなどの状況を表示します。実行しても変更を記録したりGitHubへ送ったりはしません。")
            ),
            section("GitHubとの区別",
                table(["語", "役割"], [["Git", "履歴を管理するソフトウェア"], ["local repository", "手元のPCの履歴"], ["GitHub", "リモートrepositoryの提供や共同作業を助けるサービス"]]),
                paragraph("Gitだけでもローカルで履歴を残せます。GitHubはGitの代わりとなるプログラミング言語ではありません。後でremoteとして接続すれば、手元と離れた場所のrepositoryの変更をやり取りできます。"),
                warning("「commitしたら必ずGitHubに載る」は誤りです。commitはまずローカル履歴を更新します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "Gitはバージョン管理ソフトです。", "repositoryは履歴を持ちます。",
                ".gitは通常その管理情報を置く場所です。", "分散型では手元にも履歴があります。",
                "GitHubはGitを利用するホスティングサービスです。")),
        ],
    },
    "working_tree": {
        "objective": "working treeの変更、tracked・untracked・modifiedの違いをgit statusの表示から説明できる。",
        "why": "どのファイルがまだ記録されていないか確認し、意図しないファイルを含めないためです。",
        "connection": "repositoryは履歴を持ちます。普段編集しているファイル側をworking treeと呼びます。",
        "sections": [
            section("今編集している場所",
                paragraph("working tree（作業ツリー）は、手元で現在見たり編集したりするファイル群です。trackedはGitが追跡しているファイル、untrackedはまだ追跡対象になっていないファイルです。trackedの内容を変えればmodifiedと表示されます。保存ボタンを押すこととGitの履歴へ記録することは別です。"),
                code("git status\n\n# 表示例\nmodified:   src/app.py\nUntracked files:\n  notes.txt", "app.pyは追跡済みで変更あり。notes.txtはまだ未追跡です。", "powershell"),
                table(["表示", "意味"], [["modified", "追跡済みファイルの内容が変わった"], ["untracked", "まだGitが追跡していない"], ["clean", "Gitが認識する未記録の変更がない状態"]])
            ),
            section("確認から始める",
                paragraph("コマンドで状況を確認すると、意図しないファイルの追加や更新に気付きやすくなります。例えばテストで生成された一時ファイルや個人用設定がuntrackedに出る場合があります。すべてを無条件に記録する前に、必要な変更か見極めます。"),
                flow("ファイルを編集する", "git statusで状態を見る", "追跡済みと未追跡を区別する", "次のcommitに含める候補を決める"),
                warning("「modifiedならすでにcommit済み」は誤りです。working treeでの変更はまだ履歴には入りません。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "working treeは今編集しているファイル群です。", "trackedはGitが追跡中です。",
                "untrackedは未追跡です。", "modifiedは追跡中のファイルが変わった状態です。",
                "git statusは状態を確認し、記録はしません。")),
        ],
    },
    "stage": {
        "objective": "working treeとstaging areaを区別し、git addが次のcommitの対象を選ぶことを説明できる。",
        "why": "関係のない変更を同じcommitに混ぜないためです。",
        "connection": "作業ツリーで変更を見つけました。次の記録に入れる変更を選ぶ段階を学びます。",
        "sections": [
            section("stageに載せる",
                paragraph("staging area（stage、index）は、次のcommitに含める内容を準備する場所です。git addで対象をstageします。作業ツリーの全変更が自動で含まれるわけではありません。ファイルを後からさらに編集すると、stageに置いた内容と作業ツリーの内容が異なる場合があります。"),
                code("git status\ngit add src/app.py\ngit status", "状態を確認してから、app.pyを次のcommit候補に加え、再確認します。", "powershell"),
                table(["場所", "意味"], [["working tree", "現在編集している内容"], ["stage", "次のcommitに入れる予定の内容"], ["commit", "記録された履歴"]])
            ),
            section("対象を確認する",
                paragraph("git add . は現在のディレクトリ以下の変更を広くstageします。便利ですが、関係のないファイルや秘密の設定まで含める恐れがあります。git statusで対象を確認し、必要なファイルだけを指定するか、stage後に再確認します。"),
                flow("変更を見る", "含めるファイルを選ぶ", "git addでstage", "git statusでstage内容を確かめる", "commitへ進む"),
                warning("「git addはリモートにアップロードする」は誤りです。stageはローカルの準備段階です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "stageは次のcommitに入れる内容を準備します。", "git addはstageへの追加です。",
                "作業ツリーとstageは同じ状態とは限りません。", "git add . は広く選ぶので事前・事後確認が大切です。",
                "stageだけでは履歴にもGitHubにも反映されません。")),
        ],
    },
    "commit": {
        "objective": "commitがローカル履歴へ変更を記録することを説明し、message・history・hashを初歩的に読める。",
        "why": "変更の区切りと理由を残し、後で検証できるようにするためです。",
        "connection": "stageに次の記録内容を準備しました。commitでその内容を履歴へ残します。",
        "sections": [
            section("履歴の一区切り",
                paragraph("commitはstageされた変更をひとまとまりの履歴として記録します。ある時点の状態を写した「スナップショット」と考えると分かりやすいですが、Git内部の保存形式そのものを暗記する必要はありません。commit messageには何を・なぜ変えたかを書きます。"),
                code("git commit -m \"Add database lesson\"\ngit log", "一つ目はローカルへ記録、二つ目は履歴の確認です。", "powershell"),
                paragraph("git logには各commitの識別子（hash）、作者、日時、messageなどが表示されます。hashは履歴の一件を区別する文字列です。長い値を全部覚える必要はありません。")
            ),
            section("commitとpushを分ける",
                table(["操作", "まず変わる場所"], [["git add", "ローカルのstage"], ["git commit", "ローカルのrepository"], ["git push", "接続先のremote repository"]]),
                paragraph("commitを作ってもGitHubへは自動で送られません。リモートへ共有する操作は後のUNITで扱います。小さく意味のある区切りでcommitすると、後で変更理由を追いやすくなります。"),
                warning("messageが「fix」だけでは後から何を直したか分かりにくくなります。具体的な内容を短く記します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "commitはstageされた変更を履歴へ記録します。", "messageは変更理由を伝えます。",
                "git logで過去の記録を見られます。", "hashはcommitの識別子です。",
                "commitはGitHubへの送信ではありません。")),
        ],
    },
    "branch": {
        "objective": "branchを作業の流れを分ける目印として説明し、mainと別作業の関係を理解できる。",
        "why": "新しい教材や修正を、共有している安定した作業線と分けて進めるためです。",
        "connection": "commitの履歴を学びました。branchはその履歴上の作業の流れを分けます。",
        "sections": [
            section("作業線を分ける",
                paragraph("branchは履歴上の特定のcommitを指す名前で、作業が進むと新しいcommitへ移ります。mainは代表的なbranch名の例です。別branchで第9訓練を作れば、mainとは分けて変更を積み重ねられます。後から変更を合わせる操作をmergeと呼びます。"),
                code("main:       A ─ B ─ C\n                 \\\nlesson:           D ─ E", "Bから分かれたlesson側で新しい教材のcommitを積む概念図です。"),
                table(["状態", "意味"], [["main", "基準となる作業線の例"], ["lesson", "別作業のbranch名の例"], ["merge", "分かれた変更を合わせる操作"]])
            ),
            section("分けても安全確認は必要",
                paragraph("branchはファイルの完全な別コピーを毎回作る機能と同じではありません。切り替えると作業ツリーに見える内容が変わります。未記録の変更があると切り替えに注意が必要です。初学段階では、現在どのbranchにいるかをgit statusで確認できれば十分です。"),
                warning("branchを作っただけで、テストやレビューが不要になるわけではありません。分けた作業を統合するときにも確認が必要です。"),
                note("確認例", "教材の大きな修正を別branchで行い、確認後にmainへ統合する流れを想像してください。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "branchは作業の流れを分けます。", "mainはbranch名の一例です。",
                "各branchでcommitを積めます。", "mergeは分かれた変更を合わせます。",
                "branchがあってもテストと確認は必要です。")),
        ],
    },
    "remote": {
        "objective": "local repositoryとremote repositoryを区別し、GitとGitHub、originの役割を説明できる。",
        "why": "手元の履歴を共有するとき、どこへ送るのか理解するためです。",
        "connection": "branchとcommitは手元でも使えます。次は別の場所にあるrepositoryとの関係です。",
        "sections": [
            section("離れた場所のrepository",
                paragraph("remote repositoryは別のコンピュータやサービスにあるGitのrepositoryです。GitHubはその保存や共同作業を助けるサービスの一例です。originは接続先に付ける慣例的な名前で、GitHubという意味の特別な命令ではありません。接続先のURLや名前はプロジェクトごとに異なります。"),
                code("git remote -v", "登録済みremoteの名前とURLを表示します。接続先へ送信しません。", "powershell"),
                table(["場所", "例", "主な操作"], [["local", "手元のPC", "編集・add・commit"], ["remote", "GitHub等の接続先", "共有・共同作業"]])
            ),
            section("サービスと道具",
                paragraph("Gitをローカルで使うことと、GitHubアカウントで共有することは別です。インターネットがなくても手元のcommitは作れます。共有したいときだけremoteとのやり取りが必要になります。この教材中のgit remote -vは状態を読む例で、外部通信は行いません。"),
                warning("「GitHub＝Gitそのもの」ではありません。Gitは履歴管理、GitHubはそれを利用するサービスです。"),
                note("確認例", "git logに新しいcommitが見えても、remoteに同じcommitがあるとはまだ言えません。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "localは手元、remoteは別の場所のrepositoryです。", "GitHubはremoteを提供するサービスの一例です。",
                "originはremoteによく使う名前です。", "git remote -vは登録先を確認します。",
                "手元のcommitはremoteへの共有とは別です。")),
        ],
    },
    "sync": {
        "objective": "pushとpullの向きを区別し、commit済みだがremote未反映の状態を説明できる。",
        "why": "共同作業で手元と共有先の履歴をやり取りするときの混乱を避けるためです。",
        "connection": "localとremoteを区別しました。二つの間で変更を移す基本操作を学びます。",
        "sections": [
            section("二つの向き",
                paragraph("pushはローカルのcommitをremoteへ送る操作、pullはremoteの変更を取得して現在のbranchへ反映する操作です。どちらも単なるファイルの上書きコピーではなく、Gitの履歴をやり取りします。pullの内部にある統合方法の詳細はここでは扱いません。"),
                code("git push\n# 共有先の変更を手元へ取り込む場合\ngit pull", "この例はコマンドの意味を読むためのものです。実際のremoteへは実行しません。", "powershell"),
                table(["操作", "基本の向き", "前提"], [["push", "local → remote", "共有したいcommitがある"], ["pull", "remote → local", "共有先の新しい変更を取り込む"]])
            ),
            section("今どこまで反映されたか",
                flow("作業ツリーで編集", "stageへ追加", "localでcommit", "pushでremoteへ共有", "別の作業者がpullで取得"),
                paragraph("commit済みでもpushしていなければremote側には反映されません。逆にpullだけでは自分の未共有commitを送れません。remote側に別の変更があるとpushがそのまま通らないこともあるので、表示された状態を確認してから進めます。"),
                warning("pushとpullを取り違えると、変更がどちらへ向かうか誤解します。実行前にlocalとremoteの状態を確認します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "pushはlocalからremoteへ送ります。", "pullはremoteからlocalへ取り込みます。",
                "commitだけではremoteに載りません。", "pullは自分のcommitを送る操作ではありません。",
                "共有前後に状態を確認します。")),
        ],
    },
    "gitignore": {
        "objective": ".gitignoreの用途と限界を説明し、既に追跡・共有した秘密を消せないことを理解できる。",
        "why": "キャッシュや個人設定を誤って履歴へ含めないためです。",
        "connection": "pushすると履歴を共有できます。共有してはいけないものを事前に区別します。",
        "sections": [
            section("追跡しない候補",
                paragraph(".gitignoreは、指定したパターンに一致する未追跡ファイルを通常の追加対象から外す設定ファイルです。Pythonの__pycache__、仮想環境のフォルダ、ビルド成果物、個人用の.envなどは候補です。一方、ソースコードや教材・テストは通常追跡します。"),
                code("__pycache__/\n.venv/\n.env", "この3行は.gitignoreの例です。環境ごとの生成物や秘密設定を含めない意図を示します。"),
                table(["ファイル", "考え方"], [["src/app.py", "共有するコード"], ["__pycache__/", "再生成できるキャッシュ"], [".env", "環境固有・秘密値が入り得る設定"]])
            ),
            section("ignoreの限界",
                paragraph("すでにGitで追跡されているファイルには、後から.gitignoreへ追加しても通常は追跡が続きます。過去にpushした秘密情報も自動削除されません。秘密は最初から含めない設計が重要で、漏れた場合は影響確認や値の失効・再発行など別の対応が必要です。詳細はセキュリティ訓練で学びます。"),
                warning(".gitignoreは秘密を暗号化する機能でも、過去の履歴を消す機能でもありません。"),
                note("確認例", "テスト後にできたキャッシュは再生成できます。教材本文は再生成できないので通常は履歴へ残します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                ".gitignoreは未追跡ファイルを追加対象から外します。", "キャッシュや環境固有ファイルが候補です。",
                "必要なソースと教材は追跡します。", "追跡済みファイルには後からのignoreだけでは効きません。",
                "既に共有した秘密は自動削除されません。")),
        ],
    },
    "project_files": {
        "objective": "依存ライブラリ、requirements.txt、READMEの役割を説明し、このプロジェクトの再現手順と結び付けられる。",
        "why": "別のPCや将来の自分がアプリを起動・検証できるようにするためです。",
        "connection": "共有するコードと除外する生成物を区別しました。共有すべき説明と依存情報を学びます。",
        "sections": [
            section("依存を記録する",
                paragraph("dependency（依存関係）は、自分のプログラムが動くために必要な外部ライブラリなどです。このプロジェクトではFlaskをアプリに、pytestをテストに使います。requirements.txtはPython環境へ導入するパッケージと、必要に応じてバージョンの条件を記すファイルです。実際にインストールされるバージョンは記述方法に依存します。"),
                code("Flask\npytest", "requirements.txtの概念例。実際のプロジェクトでは現在のファイルに従います。"),
                code("python -m pip install -r requirements.txt", "依存を導入するコマンド例。教材画面は実行しません。", "powershell")
            ),
            section("READMEが入口になる",
                paragraph("READMEにはプロジェクトの目的、必要環境、起動方法、テスト方法などを書きます。依存ファイルだけでは「何を作ったか」「どう使うか」は伝わりません。READMEだけでは実際のパッケージが導入されるわけでもありません。二つを合わせて、他の人が環境を再現しやすくします。"),
                table(["ファイル", "主な内容"], [["requirements.txt", "必要なPythonパッケージ"], ["README.md", "概要・起動・テストの手順"]]),
                warning("ライブラリ名をREADMEにだけ書いても、自動導入の情報にはなりません。requirements.txtの内容と説明を一致させます。")
            ),
            section("このUNITで必ず理解しておくこと", key_points(
                "依存は動作に必要な外部ライブラリなどです。", "requirements.txtはPythonパッケージの導入情報です。",
                "READMEは目的と利用手順を説明します。", "このゲームではFlaskとpytestを利用します。",
                "説明と依存情報を合わせて他環境での再現を助けます。")),
        ],
    },
    "development_cycle": {
        "objective": "自動テスト・ログの役割と限界を説明し、変更からcommit・共有までの基本サイクルを順に説明できる。",
        "why": "第1〜8訓練で学んだアプリを、壊したことに気付きながら継続して改善するためです。",
        "connection": "Gitで変更を記録する方法と、README・依存情報を学びました。最後に日常の開発作業としてつなぎます。",
        "sections": [
            section("テストとログを使う",
                paragraph("automated test（自動テスト）は決めた入力や操作について期待した結果になるかを機械的に確かめます。pytestはこのプロジェクトのテスト実行に使います。以前できていたことが変更で壊れる回帰を見つける助けになります。ただしテストしていない状況まで正しいとは保証しません。"),
                code("python -m pytest", "既存テストを実行するコマンドです。結果の失敗箇所を読んで原因を調べます。", "powershell"),
                paragraph("log（ログ）は実行中に起きた出来事の記録です。エラー時刻や処理の流れを調べる手がかりになります。Gitのcommit履歴はコード変更の記録であり、アプリ実行中のログとは目的が違います。ログへパスワードなどの秘密を不用意に書かないことも大切です。"),
                table(["記録・確認", "分かること"], [["pytest", "指定した動作が期待通りか"], ["アプリのログ", "実行中に何が起きたか"], ["Gitの履歴", "コードをどう変えたか"]])
            ),
            section("一つの開発サイクル",
                flow("仕様を確認する", "コードと教材を変更する", "git statusで変更を確かめる", "python -m pytestでテストする", "画面を手動で確かめる", "必要な変更だけgit addする", "git commitで理由とともに記録する", "共有が必要ならgit pushする"),
                paragraph("実際には作業内容やチーム方針によって順序や確認方法が変わります。テストが失敗したら原因を調べて修正し、もう一度確認します。テストが全部成功しても、教材の説明が分かりやすいか、未確認の操作に問題がないかは別に確かめる必要があります。"),
                warning("「pytestが成功した＝バグが絶対にない」は誤りです。テストは指定した条件についての証拠です。"),
                note("確認例", "教材文を直した後はテストで画面が開くことを確かめ、実際に読んで誤字や説明のつながりも確認します。")
            ),
            section("この訓練をつなげる", key_points(
                "working treeで編集し、stageを選び、commitで記録します。", "remoteへ共有するときはpushです。",
                "pytestは指定した動作を確認し、回帰発見に役立ちます。", "ログは実行中の出来事、Git履歴はコード変更の記録です。",
                "テストと手動確認の後に変更を記録します。", "テスト成功はバグゼロの保証ではありません。")),
        ],
    },
}
