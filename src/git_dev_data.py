"""正式第9訓練の節末問題と章末BOSS。Gitコマンドは出題文として表示するだけ。"""

from src.git_dev_chapters import CHAPTERS
from src.choice_order import arrange_choices


def choice(prompt, right, wrong1, wrong2, wrong3, explanation, source=None):
    item = {"type": "application", "prompt": prompt, "options": [right, wrong1, wrong2, wrong3],
            "answer": 0, "explanation": explanation}
    if source:
        item["code"] = source
    return item


def true_false(prompt, answer, explanation):
    return {"type": "true_false", "prompt": prompt, "answer": answer,
            "explanation": explanation}


def term(prompt, answer, explanation, *aliases):
    return {"type": "term", "prompt": prompt, "answer": answer,
            "accepted_answers": [answer, *aliases], "explanation": explanation}


GIT_DEV_COURSE = {
    "title": "Git・開発基礎訓練",
    "description": "変更履歴・共同作業・テストを安全な開発サイクルにつなぐ正式第9訓練。",
    "question_mode": "choice",
    "curriculum_number": 9,
    "lesson_label": "UNIT",
    "boss_name": "HISTORY KEEPER",
    "lessons": [
        {"id": "version_control", "title": "バージョン管理とは", "summary": "変更の内容と理由を記録します。", "questions": [
            choice("バージョン管理の主な目的は？", "変更の順序・内容・理由を追う", "画面を自動で装飾する", "通信速度を上げる", "DBの全行を削除する", "履歴があると、いつ何が変わったか調べられます。"),
            choice("昨日動いた画面が今日壊れた。履歴が助ける点は？", "変更差分から原因候補を探せる", "必ず自動修復する", "すべてのテストを不要にする", "エラーを必ず隠す", "差分は問題が始まった変更を探す手がかりです。"),
            choice("バックアップとバージョン管理の関係は？", "目的が重なるが別の仕組み", "完全に同じ", "どちらも不要", "履歴があれば保存先の故障対策は不要", "バックアップは紛失に備え、履歴は変更を追います。"),
            choice("変更理由を履歴に残す利点は？", "後の自分や共同作業者が判断を理解できる", "Pythonが自動で速くなる", "HTTPが不要になる", "ファイルが必ず秘密になる", "なぜ変えたかを追えるとレビューや修正に役立ちます。"),
        ]},
        {"id": "git_repo", "title": "Gitとrepository", "summary": "手元の履歴を管理します。", "questions": [
            choice("Gitとは？", "分散型バージョン管理ソフト", "GitHub専用のWebブラウザー", "Pythonの型", "SQLの列名", "Gitは履歴を管理する道具です。"),
            choice("local repositoryは？", "手元のPCにある履歴の保存場所", "常にGitHubだけ", "CSSの設定", "HTTPヘッダー", "分散型Gitでは手元にも履歴があります。"),
            choice("通常の.gitが持つものは？", "Gitの管理情報・履歴", "Web画面の色だけ", "OS本体", "PythonのRAM", ".gitはrepositoryの管理情報を保持します。"),
            choice("git statusの役割は？", "作業状態を表示する", "GitHubへ送る", "全履歴を削除する", "自動でテストする", "statusは変更やstageの状況を確認します。"),
        ]},
        {"id": "working_tree", "title": "working tree", "summary": "今編集しているファイルを見ます。", "questions": [
            choice("working treeとは？", "現在編集しているファイル群", "remote上の履歴だけ", "stageと常に同一", "pytestの結果だけ", "working treeは手元で見て編集する内容です。"),
            choice("git statusにmodified: src/app.pyが出た。意味は？", "追跡済みのapp.pyが変更された", "すでにGitHubへ送られた", "未追跡である", "commit済み", "modifiedは追跡中のファイルに未記録の変更がある状態です。"),
            choice("untracked filesにnotes.txtが出た。意味は？", "まだGitの追跡対象ではない", "必ず秘密情報", "すでにcommit済み", "remoteだけにある", "untrackedはGitがまだ追跡していないファイルです。"),
            choice("ファイルを保存した直後に正しいのは？", "Gitの履歴に入るには後でstageとcommitが必要", "自動でGitHubへpush", "必ず全テスト成功", "remoteが削除される", "エディターの保存とGit履歴への記録は別です。"),
        ]},
        {"id": "stage", "title": "stage", "summary": "次のcommitの対象を選びます。", "questions": [
            choice("git add src/app.pyは？", "app.pyの変更をstageへ加える", "remoteへ送る", "app.pyを実行する", "全履歴を削除する", "git addは次のcommit候補を準備します。"),
            choice("stageとworking treeの違いは？", "stageは次のcommit予定、working treeは現在の編集内容", "完全に同じで常に同期", "stageはGitHub", "working treeはDB", "stage後にさらに編集すると両者は異なり得ます。"),
            choice("git add .の前後に確認すべきことは？", "git statusで対象を確認する", "無条件ですべてpushする", "テスト結果を消す", "READMEを削除する", "広い範囲をstageするので意図しないファイルに注意します。"),
            choice("stageまで終えた後、まだないものは？", "新しいcommit記録", "作業ツリー", "選んだ変更", "git statusの表示", "stageは記録の準備で、commitは別の操作です。"),
        ]},
        {"id": "commit", "title": "commitとhistory", "summary": "理由とともにローカル履歴へ残します。", "questions": [
            choice("commitの主な効果は？", "stageされた変更をローカル履歴へ記録", "即GitHubへ必ず送信", "CSSだけ変更", "DBに利用者を登録", "commitはまず手元のrepositoryに記録します。"),
            choice("git commit -mのmessageに書くとよいものは？", "変更の内容や理由", "パスワード", "意味のない文字だけ", "HTTP Statusだけ", "後で履歴を読む人に意図が伝わるようにします。"),
            choice("git logで見られるものは？", "commitの履歴と識別子", "実行中のPython変数だけ", "ブラウザーのCSS", "DBの全行", "logにはcommitのhashやmessageなどが出ます。"),
            choice("commit済みでGitHub未反映なら？", "pushがまだ必要", "もう全員に共有済み", "stageから消す必要がある", "テスト不可能", "ローカルの記録とremoteへの共有は別です。"),
        ]},
        {"id": "branch", "title": "branch", "summary": "作業の流れを分けます。", "questions": [
            choice("branchの役割は？", "履歴上の作業線を分ける", "すべてのファイルを暗号化する", "テストを省く", "SQLを実行する", "branchで別の変更の流れを作れます。"),
            choice("mainとは？", "よく使われるbranch名の一例", "必須のOS名", "GitHubのパスワード", "DBの型", "mainは代表的な名前ですが、branch名はプロジェクトで異なります。"),
            choice("mergeは何を表す？", "分かれた変更を合わせる", "履歴を自動バックアップだけ", "Pythonを起動する", "HTTP Responseを返す", "mergeは別branchの変更を統合する操作です。"),
            choice("別branchで作業すれば？", "作業を分けられるがテストと確認は必要", "バグが絶対に起きない", "remoteが消える", "commitはできない", "分離と品質確認は別の役割です。"),
        ]},
        {"id": "remote", "title": "remote repositoryとGitHub", "summary": "手元と共有先を分けます。", "questions": [
            choice("remote repositoryとは？", "別の場所にあるGit repository", "手元のCSSだけ", "stageそのもの", "CPUの別名", "remoteは接続先の履歴を持つrepositoryです。"),
            choice("GitとGitHubの違いは？", "Gitは履歴管理、GitHubはその共有サービスの一例", "同一のプログラミング言語", "GitHubがOS", "Gitは画像形式", "Gitはソフトウェア、GitHubはサービスです。"),
            choice("originは通常何の名前？", "remoteに付けた名前", "常にbranch名", "Pythonの関数", "SQLの条件", "originは接続先を呼ぶ慣例的な名前です。"),
            choice("git remote -vで確認するのは？", "登録された接続先の名前とURL", "全ファイルを削除", "テスト成績", "DBの主キー", "remote -vは接続先の設定を表示します。"),
        ]},
        {"id": "sync", "title": "push・pull", "summary": "履歴のやり取りの向きを学びます。", "questions": [
            choice("pushの基本方向は？", "localからremote", "remoteからlocal", "HTMLからCSS", "DBからCPU", "pushは手元のcommitを共有先へ送ります。"),
            choice("pullの基本方向は？", "remoteからlocal", "localからremote", "stageからCPU", "READMEからSQL", "pullは共有先の変更を取り込みます。"),
            choice("commit後に共有先が更新されていない。次に必要なのは？", "状況を確認してpush", "もう一度HTMLを開くだけ", "pullだけで送信", "stageを削除", "commitはローカル、pushはremoteへの共有です。"),
            choice("git pullを実行すると自分の未共有commitは？", "それだけではremoteへ送られない", "必ずremoteへ送られる", "必ず消える", "HTMLになる", "pullは取り込み方向です。"),
        ]},
        {"id": "gitignore", "title": ".gitignore", "summary": "履歴に含めないものを区別します。", "questions": [
            choice(".gitignoreの主な用途は？", "指定した未追跡ファイルを通常の追加対象から外す", "すべての履歴を消す", "秘密を暗号化する", "GitHubへ送信する", "ignoreは追跡対象の選別に使います。"),
            choice("追跡しない候補として自然なのは？", "__pycache__や個人用.env", "教材の原本すべて", "src/app.pyだけ", "READMEだけ", "再生成可能なものや環境固有・秘密設定が候補です。"),
            choice("既に追跡中の.envを.gitignoreへ書くと？", "それだけでは追跡は止まらない", "過去の履歴から自動で消える", "秘密が暗号化される", "remoteが削除される", "追跡済みファイルにはignoreの追加だけでは通常効きません。"),
            choice("過去にpushした秘密への対応は？", "ignoreだけでは消えず、影響確認や値の失効などが必要", "ignoreだけで完全解決", "テストを消せば解決", "READMEを隠せば解決", "共有済みの秘密は別途対応が必要です。"),
        ]},
        {"id": "project_files", "title": "dependency・requirements.txt・README", "summary": "環境の再現と利用手順を残します。", "questions": [
            choice("dependencyとは？", "動作に必要な外部ライブラリなど", "Gitのbranchだけ", "DBの全行", "HTTP 404", "このゲームではFlaskやpytestが依存の例です。"),
            choice("requirements.txtの主な役割は？", "Pythonパッケージの導入情報を示す", "画面を描画する", "Gitの履歴を表示", "DBを削除", "他環境で必要なパッケージを導入する手がかりです。"),
            choice("READMEに書くとよいものは？", "概要・起動・テスト方法", "パスワードの実値", "CPUの設計図だけ", "全DBの個人情報", "READMEはプロジェクトの入口です。"),
            choice("requirementsとREADMEの違いは？", "前者は依存情報、後者は目的と使い方", "完全に同じ", "前者だけで全説明が伝わる", "後者だけで自動インストール", "双方を揃えると再現しやすくなります。"),
        ]},
        {"id": "development_cycle", "title": "test・log・開発サイクル", "summary": "変更を検証し履歴へ残します。", "questions": [
            choice("python -m pytestの役割は？", "自動テストを実行", "GitHubへpush", "DBを初期化", "HTMLを装飾", "pytestは指定された期待動作を確かめます。"),
            choice("テストが全部成功したら？", "確認した条件では期待通りだが未確認の問題は残り得る", "バグが絶対ない", "手動確認は常に不要", "commit済みになる", "テストの証拠は実際に確認した範囲に限られます。"),
            choice("アプリログとGit履歴の違いは？", "前者は実行中の出来事、後者はコード変更", "完全に同じ", "どちらもCSS", "どちらも秘密を保存すべき", "ログは実行を、Gitは変更を調べる手がかりです。"),
            choice("変更後の自然な順番は？", "状態確認→テスト→手動確認→add→commit", "commit→変更→確認不要", "push→変更→テストなし", "log削除→DB削除", "変更を確認し検証してから記録します。"),
        ]},
    ],
    "boss": [
        true_false("Gitの履歴があれば、別場所へのバックアップは必ず不要になる。", "false", "履歴追跡と障害・紛失への備えは役割が違います。"),
        term("現在編集しているファイル群を指す英語の用語は？", "working tree", "working treeは手元で編集する内容です。", "workingtree"),
        choice("modifiedとuntrackedの違いは？", "前者は追跡済みの変更、後者は未追跡", "どちらもpush済み", "前者だけGitHub", "完全に同じ", "git statusの二つの表示は追跡状態が違います。", "modified: src/app.py\nUntracked files: notes.txt"),
        choice("app.pyと個人設定を編集した。次のcommitにapp.pyだけ入れるには？", "状態を確認してapp.pyをgit add", "git add .を無確認で使う", "個人設定を先にpush", "git pullだけ行う", "stageで必要な変更だけ選びます。"),
        true_false("git addした変更は、その時点でGitHubへ公開される。", "false", "addはローカルstageへの準備です。"),
        choice("commitは済んだがGitHubにない。現在の状態は？", "ローカル履歴にあり、pushはまだ", "remoteだけにある", "未追跡のまま", "テストが必ず失敗", "commitとpushは異なる段階です。"),
        term("commit履歴を確認するGitのコマンドを入力してください。", "git log", "git logはcommit履歴を表示します。"),
        choice("branchを作る主な目的は？", "作業線を分けて変更を進める", "テストを廃止する", "秘密を暗号化する", "DBを削除する", "branchは履歴上の作業の流れを分けます。"),
        true_false("GitとGitHubは完全に同じソフトウェアである。", "false", "Gitは履歴管理ソフト、GitHubは共有サービスの一例です。"),
        choice("共有先の新しいcommitを手元へ取り込む方向は？", "pull", "push", "add", "commit", "pullはremoteからlocalへの取り込みです。"),
        choice(".gitignoreへ.envを追加した。過去にpush済みの秘密は？", "自動削除されず別の対応が必要", "過去の全履歴から自動消去", "自動で暗号化", "pullだけで消える", "ignoreは過去の履歴を消す機能ではありません。"),
        choice("別PCでこのアプリを再現する資料の組み合わせは？", "READMEとrequirements.txt", "CSSだけ", "git logだけ", "HTTP 200だけ", "起動手順と依存情報の両方が必要です。"),
        true_false("pytestが成功すれば、未テストの画面にもバグは絶対にない。", "false", "成功はテストした条件についての結果です。"),
        choice("app.pyを修正し、個人設定ファイルも作った。共有前の流れとして適切なのは？", "statusで差分を把握→テスト→app.pyだけstage→commit→必要ならpush", "statusを省いて全ファイルをstage→commit→後で秘密を確認", "テスト前に個人設定もcommitし、.gitignoreで過去の履歴から消す", "commit前にpushすれば作業ツリーの変更だけを共有できる", "状態とテスト結果を確認し、共有すべき変更だけをstageして履歴に残します。"),
    ],
}

for lesson in GIT_DEV_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])

arrange_choices(GIT_DEV_COURSE)

for question in (
    [item for lesson in GIT_DEV_COURSE["lessons"] for item in lesson["questions"]]
    + GIT_DEV_COURSE["boss"]
):
    if "options" in question:
        right = question["options"][question["answer"]]
        question["wrong_explanations"] = {
            str(index): f"「{option}」はこの状態・操作と合いません。{question['explanation']} 正しい選択肢は「{right}」です。"
            for index, option in enumerate(question["options"]) if index != question["answer"]
        }
