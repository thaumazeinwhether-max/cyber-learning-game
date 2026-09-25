"""正式第7訓練の節末問題と章末BOSS。コードはAST解析のみで採点する。"""

from src.flask_basics_chapters import CHAPTERS


def code_question(prompt, answer, explanation, *alternatives):
    item = {"prompt": prompt, "answer": answer, "explanation": explanation}
    if alternatives:
        item["accepted_answers"] = list(alternatives)
    return item


def choice(prompt, options, answer, explanation, source=None):
    item = {"mode": "choice", "prompt": prompt, "options": options,
            "answer": answer, "explanation": explanation}
    if source:
        item["code"] = source
    return item


def review(prompt, source, valid, explanation, answer=None, alternatives=()):
    item = {"type": "debug", "prompt": prompt, "code": source,
            "valid": valid, "explanation": explanation}
    if answer is not None:
        item["answer"] = answer
    if alternatives:
        item["accepted_answers"] = list(alternatives)
    return item


def boss_choice(prompt, options, answer, explanation, source=None):
    item = choice(prompt, options, answer, explanation, source)
    item["type"] = "application"
    return item


FLASK_BASICS_COURSE = {
    "title": "Flask・Webアプリ基礎訓練",
    "description": "Python・HTTP・HTMLを統合し、FlaskのRequestからResponseまでを学ぶ正式訓練。",
    "question_mode": "code",
    "curriculum_number": 7,
    "lesson_label": "UNIT",
    "boss_name": "WEB APP CORE",
    "lessons": [
        {"id": "framework", "title": "Webフレームワークとは", "summary": "共通処理とアプリ固有処理を分けます。", "questions": [
            choice("Webフレームワークが助ける共通処理は？", ["URLと関数の対応", "利用者の学習意欲の自動生成", "教材内容の正しさの保証", "すべての画面設計の自動完成"], 0, "ルーティング等を助けますが、アプリ固有の判断は開発者が書きます。"),
            choice("回答の正誤判定を決める主な場所は？", ["アプリ固有の処理", "フレームワークが自動で決定", "CSS", "DNS"], 0, "教材と採点基準はアプリが決めます。"),
            choice("ブラウザーがRequestを送った後の基本順は？", ["経路判定→アプリ関数→Response", "CSS→CPU停止→Response", "Response→Request", "HTMLだけで判定"], 0, "フレームワークが経路を選び、関数の結果を応答にします。"),
            choice("フレームワークの説明として適切なのは？", ["共通のWeb処理を整理する道具", "Webサイトの全内容を自動生成", "Pythonの代替OS", "画像の保存形式"], 0, "共通機能の土台を提供します。"),
        ]},
        {"id": "flask", "title": "Flaskとは", "summary": "アプリオブジェクトを作ります。", "questions": [
            code_question("Flaskクラスを読み込む1行を書いてください。", "from flask import Flask", "FlaskからクラスFlaskをimportします。"),
            code_question("Flaskが読み込み済みです。appというFlaskアプリを作ってください。", "app = Flask(__name__)", "__name__を渡してアプリオブジェクトを作ります。"),
            choice("app = Flask(__name__)のappは？", ["アプリを表す変数", "HTTPステータス", "CSSファイル", "DNSサーバー"], 0, "appがFlaskアプリオブジェクトを参照します。"),
            choice("Flaskアプリを作っただけで完成するものは？", ["まだ各URLの処理は必要", "すべての教材ページ", "すべてのテスト", "ユーザー認証"], 0, "アプリ生成後、routeや画面を登録します。"),
        ]},
        {"id": "structure", "title": "Flaskアプリの基本構造", "summary": "Python・templates・staticの役割を分けます。", "questions": [
            choice("lesson.htmlの置き場所として自然なのは？", ["templates", "staticだけ", "CPU", "testsだけ"], 0, "HTMLのひな形はtemplatesに置きます。"),
            choice("style.cssの置き場所として自然なのは？", ["static", "templatesだけ", "session", "route"], 0, "CSSは静的ファイルとして配信します。"),
            choice("src/learn_routes.pyの主な役割は？", ["URLに応じたPython処理", "CSSの色指定だけ", "画像だけ", "HTMLの見出しだけ"], 0, "ルートと進行の処理をPythonで定義します。"),
            choice("テンプレートと静的ファイルの違いは？", ["HTML生成のひな形と、そのまま配信するCSS等", "完全に同じ", "どちらもCPU", "どちらもDNS"], 0, "テンプレートは値を埋めてHTMLを生成し、staticはCSS等を配信します。"),
        ]},
        {"id": "route", "title": "Route", "summary": "URLをPython関数へ結び付けます。", "questions": [
            code_question("appが定義済みです。/へGETが来たらHelloを返すindex関数を書いてください。", "@app.route('/')\ndef index():\n    return 'Hello'", "@app.routeが/と関数を結び、returnが応答に使う値を返します。"),
            choice("次のコードでindex関数が呼ばれるのは？", ["対応する/へのRequest時", "定義直後に無限に", "CSS変更時だけ", "画像保存時だけ"], 0, "Flaskが/の要求を受けると登録済みの関数を呼びます。", "@app.route('/')\ndef index():\n    return 'Hello'"),
            choice("print('Hello')だけを使うとブラウザーへ返る？", ["返り値とは別なので代わりにならない", "必ずHelloページになる", "HTMLへ自動変換される", "DNSが返す"], 0, "ブラウザーへの応答には関数のreturnが必要です。"),
            code_question("appが定義済みです。/pingへGETが来たらpongを返すping関数を書いてください。", "@app.route('/ping')\ndef ping():\n    return 'pong'", "パスと関数をrouteで対応付けます。"),
        ]},
        {"id": "url_route", "title": "URLとRoute", "summary": "URLパスから応答までを追います。", "questions": [
            choice("https://example.com/learn/でFlaskのRouteが主に対応する部分は？", ["/learn/", "example.comだけ", "httpsだけ", "IPの全桁"], 0, "RouteはURLのパスに対応します。"),
            code_question("appが定義済みです。/learn/へ要求が来たら訓練一覧を返すlearn_home関数を書いてください。", "@app.route('/learn/')\ndef learn_home():\n    return '訓練一覧'", "/learn/を登録し、関数で応答を返します。"),
            choice("未登録のURLパスへ要求したとき通常返るのは？", ["404", "200", "必ず500", "必ず302"], 0, "対応するルートがなければ通常404です。"),
            choice("URLパスと物理ファイルの関係は？", ["必ず一対一ではない", "常に同じ", "Routeとは無関係", "DNSがファイルを作る"], 0, "Flaskの関数がパスに応じて動的に応答できます。"),
        ]},
        {"id": "template", "title": "Template", "summary": "render_templateでHTMLを返します。", "questions": [
            code_question("Flaskからrender_templateを読み込む1行を書いてください。", "from flask import render_template", "HTMLのひな形を使う関数をimportします。"),
            code_question("render_templateが読み込み済みです。index.htmlを返すindex関数を書いてください。", "def index():\n    return render_template('index.html')", "関数のreturnでテンプレートから作ったHTMLを返します。"),
            choice("index.htmlの通常の置き場所は？", ["templates", "static", "CPU", "session"], 0, "Flaskのテンプレートは通常templatesフォルダへ置きます。"),
            choice("長いHTMLをPythonのreturn文字列へ直書きする代わりに使うのは？", ["テンプレート", "DNS", "ポート番号", "RAM"], 0, "処理と画面の構造を分けられます。"),
        ]},
        {"id": "jinja", "title": "Jinja基礎", "summary": "Pythonの値をHTMLへ表示します。", "questions": [
            code_question("render_templateが読み込み済みです。index.htmlへtitle='防衛学校'を渡して返すindex関数を書いてください。", "def index():\n    return render_template('index.html', title='防衛学校')", "キーワード引数titleがテンプレート側で使えます。"),
            choice("テンプレートの{{ title }}が表すのは？", ["渡された値を表示", "HTTPのStatus Code", "CSSセレクタ", "DNS名"], 0, "Jinjaの{{ }}は値を表示する場所です。", "<h1>{{ title }}</h1>"),
            choice("{% if complete %}が行うことは？", ["条件に応じたHTML生成", "Pythonコードの任意実行", "IP変更", "CSSの圧縮"], 0, "Jinjaのifはサーバー側で表示条件を扱います。"),
            choice("Jinjaの処理が行われる場所は？", ["サーバー側", "ブラウザーのCSSだけ", "ルーター", "画像内"], 0, "サーバーがテンプレートを処理してHTMLを返します。"),
        ]},
        {"id": "static", "title": "Static files", "summary": "CSSや画像を別のRequestで配信します。", "questions": [
            choice("style.cssの種類は？", ["静的ファイル", "ルート関数", "Session", "BOSS問題"], 0, "CSSはstaticへ置く静的ファイルの例です。"),
            choice("HTMLでCSSを参照すると、ブラウザーは？", ["CSSを追加でRequestできる", "Python関数を直接編集する", "DNSを削除する", "必ずSessionを初期化する"], 0, "HTMLのlink先を追加取得します。"),
            code_question("Flaskのurl_forが読み込み済みです。static内style.cssのURLを作る式を1行で書いてください。", "url_for('static', filename='style.css')", "staticエンドポイントとfilenameを指定します。"),
            choice("テンプレートとstaticについて正しいのは？", ["テンプレートはHTML生成、staticはCSS等の配信", "完全に同じ", "どちらもPythonの関数", "staticだけで自動表示"], 0, "HTMLからCSSを参照して配信します。"),
        ]},
        {"id": "request_form", "title": "Requestとform data", "summary": "フォームのnameとrequest.formをつなぎます。", "questions": [
            code_question("Flaskからrequestを読み込む1行を書いてください。", "from flask import request", "現在のHTTP Requestを扱うrequestをimportします。"),
            code_question("requestが読み込み済みです。answerという送信値を、なければ空文字としてvalueへ代入してください。", "value = request.form.get('answer', '')", "フォームのname=answerに対応する値を読みます。"),
            choice("HTMLのname='answer'と対応するFlask側は？", ["request.form.get('answer')", "request.form.get('id')だけ", "CSSのanswer", "DNSのanswer"], 0, "送信データの名前で値を探します。"),
            choice("request.formの値について適切なのは？", ["受け取った後も確認が必要", "必ず正しい", "必ず整数", "サーバーでは読めない"], 0, "利用者は値を改変できるので検証します。"),
        ]},
        {"id": "methods_redirect", "title": "GET / POSTとRedirect", "summary": "メソッドを分け、送信後に別ページへ移ります。", "questions": [
            code_question("appが定義済みです。/submitでGETとPOSTを受け付け、okを返すsubmit関数を書いてください。", "@app.route('/submit', methods=['GET', 'POST'])\ndef submit():\n    return 'ok'", "methodsへ二つのHTTPメソッドを指定します。"),
            code_question("requestが読み込み済みです。POSTならTrue、それ以外はFalseを返すis_post関数を書いてください。", "def is_post():\n    if request.method == 'POST':\n        return True\n    return False", "request.methodがPOSTか比較し、返り値を分けます。", "def is_post():\n    return request.method == 'POST'"),
            choice("Redirectの後に起きることは？", ["ブラウザーが移動先へ新しいRequest", "Pythonの関数が画面を直接描く", "CSSがPOSTを再送", "DNSがSessionを削除"], 0, "redirectのResponseを受けたブラウザーが移動先へ要求します。"),
            code_question("redirectとurl_forが読み込み済みです。doneへ移るgo関数を書いてください。", "def go():\n    return redirect(url_for('done'))", "url_forで移動先URLを作り、redirectのResponseを返します。"),
        ]},
        {"id": "session_config", "title": "Session・環境変数・設定値", "summary": "状態と設定をコードから適切に分けます。", "questions": [
            code_question("Flaskからsessionを読み込む1行を書いてください。", "from flask import session", "Sessionを扱うオブジェクトをimportします。"),
            code_question("sessionが読み込み済みです。completedへTrueを保存してください。", "session['completed'] = True", "要求をまたぐ修了状態を記録します。"),
            code_question("osが読み込み済みです。環境変数LEARN_DEV_SHORTCUTを読んで値をmodeへ入れてください。", "mode = os.environ.get('LEARN_DEV_SHORTCUT')", "環境変数から設定を読みます。"),
            code_question("appが定義済みです。公開してよい設定ENABLE_HINTSへTrueを保存してください。", "app.config['ENABLE_HINTS'] = True", "app.configがFlaskアプリの設定値をまとめます。"),
            choice("Flask標準の署名付きCookie型Sessionで正しいのは？", ["署名は改ざん検知で暗号化ではない", "秘密情報を自由に保存してよい", "secret keyが不要", "必ずサーバーメモリのみ"], 0, "署名付きCookieに秘密を入れず、secret keyを守ります。"),
        ]},
        {"id": "testing", "title": "Webアプリのテスト", "summary": "test clientで200と内容を確認します。", "questions": [
            code_question("clientが定義済みです。/へGETした結果をresponseへ保存してください。", "response = client.get('/')", "test clientがアプリの/へ要求を送ります。"),
            code_question("responseが定義済みです。HTTP 200であることをassertしてください。", "assert response.status_code == 200", "status_codeが成功の番号200であるか確認します。"),
            choice("HTTP 200だけで保証されることは？", ["その応答が成功と分類されたこと", "全リンクが正しいこと", "全教材が正しいこと", "セキュリティが完璧なこと"], 0, "200はHTTP上の成功で、内容品質は別途確認します。"),
            choice("コード変更後に既存ページを再テストする理由は？", ["回帰による故障を見つける", "CPUを高速化する", "画像を変換する", "DNSを作る"], 0, "回帰テストは既存機能が壊れていないか確認します。"),
        ]},
    ],
    "boss": [
        review("要件：Flaskアプリをappへ作る。正しいか？", "from flask import Flask\napp = Flask(__name__)", True, "Flaskを読み込み、アプリオブジェクトを作っています。"),
        review("前提：appは定義済み。要件：/へ来たらHelloをブラウザーへ返す。正しいか？", "@app.route('/')\ndef index():\n    print('Hello')", False, "printはサーバー側の出力で、応答の返り値ではありません。", "@app.route('/')\ndef index():\n    return 'Hello'"),
        boss_choice("GET /learn/が届くと何が起こる？", ["登録済みrouteが対応するPython関数を呼ぶ", "HTMLファイル名だけで必ず処理", "DNSが教材を採点", "CSSが関数を呼ぶ"], 0, "RouteがURLパスと関数を結びます。", "@app.route('/learn/')\ndef learn_home():\n    return '一覧'"),
        review("前提：render_templateは読み込み済み。要件：index関数でindex.htmlのHTMLを返す。正しいか？", "def index():\n    return render_template('index.html')", True, "テンプレートからHTMLを生成して返します。"),
        boss_choice("Pythonがtitle='防衛学校'を渡したとき、何が表示される？", ["防衛学校", "{{ title }}という文字だけ", "CSS", "HTTP 404"], 0, "Jinjaが渡されたtitleをHTMLへ表示します。", "<h1>{{ title }}</h1>"),
        boss_choice("style.cssの役割と取得方法は？", ["staticのCSSをブラウザーが追加取得", "テンプレート関数として自動実行", "Sessionにだけ保存", "Request不要"], 0, "HTMLが参照するとブラウザーがstaticのURLを要求します。", "<link rel=\"stylesheet\" href=\"/static/style.css\">"),
        review("前提：requestは読み込み済み。要件：formのanswerを読みvalueへ入れる。正しいか？", "value = request.form.get('answer', '')", True, "name=answerに対応する値を読みます。"),
        review("前提：appは定義済み。要件：POSTだけを受け付ける/answerのrouteを作る。正しいか？", "@app.route('/answer', methods=['GET'])\ndef answer():\n    return 'ok'", False, "GETだけではPOSTを受け付けません。methodsをPOSTにします。", "@app.route('/answer', methods=['POST'])\ndef answer():\n    return 'ok'"),
        review("前提：request、redirect、url_forは読み込み済み。要件：handle関数で、POSTならdoneへredirectし、GETなら入力画面を返す。正しいか？", "def handle():\n    if request.method == 'POST':\n        return redirect(url_for('done'))\n    return '入力画面'", True, "POST判定後はredirectし、それ以外は画面を返します。"),
        boss_choice("Flask標準Sessionとsecret keyについて正しいのは？", ["署名付きCookieの改ざん検知にsecret keyを使う", "署名は内容を暗号化する", "秘密値をCookieへ直書きしてよい", "secret keyはCSS用"], 0, "署名は改ざん検知で、暗号化ではありません。"),
        boss_choice("環境変数を使う理由と限界は？", ["設定をコードから分けられるが、それだけで秘密は守れない", "設定は必ず公開される", "すべての認証が不要になる", "CSSが自動生成される"], 0, "環境変数は設定分離の方法の一つで、管理方法にも注意します。"),
        review("前提：test clientが定義済み。要件：/のHTTP 200を確認する。正しいか？", "response = client.get('/')\nassert response.status_code == 200", True, "GETで応答を取得し、status_codeを確認します。"),
        review("前提：test clientが定義済み。要件：/のHTTP 200を確認する。正しいか？", "response = client.get('/')\nassert response.status_code == 404", False, "404はNot Foundです。成功なら200と比較します。", "response = client.get('/')\nassert response.status_code == 200"),
        boss_choice("ブラウザーから画面表示までの正しい順序は？", ["Request→Flask Route→Python関数→Template→Response→ブラウザー", "CSS→DNS→Templateだけ", "Response→Request→Route", "Sessionだけで画面生成"], 0, "Python・HTTP・テンプレートの役割が一連の流れでつながります。"),
    ],
}

for lesson in FLASK_BASICS_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])

for lesson_number, lesson in enumerate(FLASK_BASICS_COURSE["lessons"]):
    for question_number, question in enumerate(lesson["questions"]):
        if question.get("mode") == "choice":
            offset = (lesson_number + question_number) % 4
            question["options"] = question["options"][offset:] + question["options"][:offset]
            question["answer"] = (question["answer"] - offset) % 4
for question_number, question in enumerate(FLASK_BASICS_COURSE["boss"]):
    if question.get("mode") == "choice":
        offset = question_number % 4
        question["options"] = question["options"][offset:] + question["options"][:offset]
        question["answer"] = (question["answer"] - offset) % 4

for question in (
    [item for lesson in FLASK_BASICS_COURSE["lessons"] for item in lesson["questions"]]
    + FLASK_BASICS_COURSE["boss"]
):
    if question.get("mode") == "choice":
        correct_option = question["options"][question["answer"]]
        question["wrong_explanations"] = {
            str(index): f"「{option}」では、ここで求める「{correct_option}」の役割・結果を表せません。{question['explanation']}"
            for index, option in enumerate(question["options"])
            if index != question["answer"]
        }
