"""正式第7訓練「Flask・Webアプリ基礎」の参考書型教材。"""

from src.chapter_blocks import code, flow, key_points, note, paragraph, section, table, warning


CHAPTERS = {
    "framework": {
        "objective": "Webフレームワークが共通処理をまとめる理由と、アプリ側で作る処理の範囲を説明できる。",
        "why": "HTTPの受信・経路判定・画面生成を毎回最初から作らず、目的の機能に集中するためです。",
        "connection": "Python、HTTP、HTMLを学びました。これらを一つのWebアプリとして組み合わせます。",
        "sections": [
            section("共通部分を扱う道具",
                paragraph("Webフレームワークは、Webアプリに共通する仕組みを提供するソフトウェアです。URLと処理を結ぶルーティング、RequestとResponseの扱い、テンプレートとの連携、Sessionなどの機能を利用できます。これらを使っても、アプリ固有の教材・採点・進捗は開発者が設計します。"),
                table(["フレームワークが助けること", "アプリが決めること"], [["経路と関数の対応", "どのURLで何をするか"], ["要求・応答の扱い", "入力をどう確認し結果を返すか"], ["テンプレート連携", "画面に何を表示するか"]])
            ),
            section("RequestからResponseへ",
                flow("ブラウザーがRequestを送る", "フレームワークが経路を選ぶ", "アプリの関数が処理する", "Responseを返す"),
                paragraph("フレームワークを使えばページが自動的に完成するわけではありません。教材ページを表示する関数や、回答を採点する関数は自分で書きます。フレームワークは共通の接続部分を整理する道具です。"),
                note("具体例", "このゲームではFlaskがURLと関数を結び、Learnの教材データと採点処理はsrc内のコードで定義しています。"),
                warning("『フレームワーク＝Webサイトを自動生成するもの』と覚えると、アプリ固有の処理の必要性を見落とします。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("フレームワークは共通のWeb処理を助けます。", "ルートがURLと処理を結びます。", "RequestとResponseの扱いを助けます。", "アプリ固有の判断は開発者が書きます。", "テンプレートやSessionとも連携できます。")),
        ],
    },
    "flask": {
        "objective": "FlaskをPythonのWebフレームワークとして説明し、アプリオブジェクトを作る2行を読める。",
        "why": "後のrouteやtemplateがどのアプリに登録されるか理解するためです。",
        "connection": "Webフレームワークの役割を学びました。ここから具体的にFlaskを使います。",
        "sections": [
            section("Flaskアプリを作る",
                paragraph("FlaskはPythonでWebアプリを作るためのフレームワークです。小さな構成から始め、必要な機能を組み合わせられます。まずFlaskクラスを読み込み、アプリオブジェクトを作ります。"),
                code("from flask import Flask\n\napp = Flask(__name__)", "1行目はFlaskをimportし、3行目でこのアプリを表すappを作ります。__name__はFlaskがアプリの位置を知る手掛かりです。", "python"),
                table(["部分", "意味"], [["from flask import Flask", "Flaskクラスを読み込む"], ["app", "このWebアプリを表す変数"], ["Flask(__name__)", "Flaskアプリの生成"]])
            ),
            section("アプリは組み立てて動かす",
                paragraph("アプリを作っただけではページはまだありません。次のUNIT以降でURLと関数を結び、テンプレートや静的ファイルを使って応答を作ります。開発中の起動にはpython -m src.appなどを使いますが、起動方法とアプリの仕組みは分けて考えます。"),
                note("具体例", "このプロジェクトのsrc/app.pyがFlaskアプリを作り、Learnのルートを登録します。"),
                warning("__name__のPython内部の詳細へ深入りする必要はありません。ここではFlaskが場所を把握するために渡す値と理解します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("FlaskはPythonのWebフレームワークです。", "importでFlaskを読み込みます。", "Flask(__name__)でアプリを作ります。", "appはアプリオブジェクトです。", "アプリ作成だけではページは完成しません。")),
        ],
    },
    "structure": {
        "objective": "srcのPythonコード、templatesのHTML、staticのCSS等の役割分担を説明できる。",
        "why": "画面の内容や見た目をPythonファイルへ大量に詰めず、変更箇所を探しやすくするためです。",
        "connection": "Flaskアプリを作りました。次はWebアプリのファイルがどの役割を持つか見ます。",
        "sections": [
            section("三つの置き場所",
                code("src/\n├─ app.py\n├─ learn_routes.py\n├─ templates/\n│  └─ lesson.html\n└─ static/\n   └─ style.css", "Pythonのアプリ・ルート、HTMLテンプレート、CSSの静的ファイルを分けた例です。", "text"),
                paragraph("Pythonコードは要求の処理やデータを扱います。templatesのHTMLは画面の構造、staticのCSSやJavaScript、画像はブラウザーが取得するファイルです。区別すると、文章を直す場所と処理を直す場所を見つけやすくなります。"),
                table(["場所", "例", "主な役割"], [["Pythonコード", "app.py", "アプリ生成や処理"], ["templates", "lesson.html", "画面のHTML"], ["static", "style.css", "見た目を指定"]])
            ),
            section("一つのページを組み立てる",
                flow("URLへRequest", "Pythonのルート関数が処理", "必要な値をテンプレートへ渡す", "HTMLをResponseで返す", "ブラウザーがCSSを取得"),
                paragraph("HTMLテンプレートを置いただけでは、そのページをどのURLで返すか決まりません。Python側のルートがrender_templateを呼びます。CSSもstaticに置いた後、HTMLから参照されて初めてブラウザーが読み込みます。"),
                warning("templatesとstaticは同じものではありません。前者はサーバーが値を埋めてHTMLを作るため、後者はファイルとして配信するために使います。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("Pythonコードは処理を担当します。", "templatesはHTMLのひな形です。", "staticはCSS等のファイルです。", "ルートがテンプレートを返します。", "HTMLが静的ファイルを参照します。")),
        ],
    },
    "route": {
        "objective": "@app.routeと関数の関係を読み、URLにRequestが来たとき何が実行されるか説明できる。",
        "why": "Webアプリの『どのURLでどの処理』という対応を理解するためです。",
        "connection": "ファイル構成を学びました。次はPythonコード内で処理の入口を定めます。",
        "sections": [
            section("URLを関数へ結び付ける",
                code("@app.route('/')\ndef index():\n    return 'Hello'", "1行目が/へのルート登録、2行目が対応する関数、3行目が返す内容です。", "python"),
                paragraph("routeはURLのパスとPython関数を対応付けます。@app.route('/')はデコレーターという書式で、ここでは『/への要求で下の関数を使う登録』と理解してください。装飾の内部実装は今は不要です。"),
                flow("GET /が届く", "Flaskが登録されたrouteを探す", "index関数を呼ぶ", "Helloを含むResponseを返す")
            ),
            section("呼び出しと戻り値",
                paragraph("関数を定義しただけで毎秒実行されるわけではありません。対応するRequestが届くとFlaskが呼びます。returnはFlaskへ応答に使う値を渡します。Python基礎Ⅱのreturnと同じく、単にprintしただけではブラウザーへページを返せません。"),
                table(["行", "役割"], [["@app.route('/')", "経路の登録"], ["def index():", "処理の定義"], ["return 'Hello'", "応答に使う値"]]),
                warning("print('Hello')はサーバー側の出力であり、ブラウザーへ返すResponseの代わりではありません。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("routeはURLと関数を結び付けます。", "@app.routeはその登録です。", "Requestが来たとき関数が呼ばれます。", "returnが応答に使う値を渡します。", "printとreturnは違います。")),
        ],
    },
    "url_route": {
        "objective": "URLのパスとFlaskのRouteを対応させ、未登録のURLで404になり得ることを説明できる。",
        "why": "画面のリンク先とサーバー側の処理をつなげて考えるためです。",
        "connection": "第4訓練でURLのホスト名とパスを学び、前のUNITでrouteを学びました。両者を対応させます。",
        "sections": [
            section("URLのパスで処理を選ぶ",
                paragraph("https://example.com/learn/ のホスト名は通信先を示し、/learn/というパスをサーバーへ要求します。Flaskでは対応するrouteが登録されていれば、その関数で応答します。URLのパスはディスク上の物理ファイル名と必ずしも一致しません。"),
                code("@app.route('/learn/')\ndef learn_home():\n    return '訓練一覧'", "GET /learn/が届くとlearn_homeが呼ばれ、訓練一覧を返します。", "python"),
                flow("ブラウザーのGET /learn/", "Flaskが/learn/のrouteを探す", "learn_homeを呼ぶ", "Responseを返す")
            ),
            section("登録がない場合",
                paragraph("要求されたパスに対応するルートがなければ、通常404 Not Foundになります。同じ名前に見えても、末尾のスラッシュや設定によって転送や異なる扱いになる場合があります。この教材では登録したパスとアクセスしたパスの対応を確認します。"),
                table(["要求", "登録済みなら", "未登録なら"], [["/learn/", "対応する関数で応答", "通常404"]]),
                warning("DNSでサーバーへ到達したことと、要求したURLパスの処理が存在することは別です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("URLのホスト名は通信先です。", "パスはサーバーへ求める場所です。", "FlaskのRouteがパスと関数を結びます。", "対応する処理がなければ通常404です。", "URLパスは物理ファイル名とは限りません。")),
        ],
    },
    "template": {
        "objective": "render_templateでHTMLテンプレートを返す流れを説明し、Python文字列へのHTML直書きとの違いを示せる。",
        "why": "処理と画面を分けて、教材や画面を安全に読みやすく管理するためです。",
        "connection": "Routeで関数へ進めるようになりました。次は関数からHTMLページを返します。",
        "sections": [
            section("HTMLをひな形にする",
                paragraph("テンプレートは、サーバーが値を埋めてHTMLを作るためのひな形です。Flaskのrender_template('index.html')は、通常templatesフォルダ内のファイルを読み、HTMLの応答を作ります。長いHTMLをPythonのreturn文字列へ直接書くより、役割を分けられます。"),
                code("from flask import render_template\n\n@app.route('/')\ndef index():\n    return render_template('index.html')", "importで関数を読み、/のrouteでindex.htmlを使った応答を返します。", "python"),
                table(["Python側", "テンプレート側"], [["どの画面を返すか決める", "HTMLの構造を定義"], ["値を渡す", "値を表示する位置を用意"]])
            ),
            section("応答になるまで",
                flow("Requestがrouteへ届く", "関数がrender_templateを呼ぶ", "テンプレートからHTMLを作る", "FlaskがResponseとして返す"),
                paragraph("テンプレートのファイル名が正しくても、対応するrouteがなければブラウザーがURLで直接開けるとは限りません。ページはルート関数が返します。値を埋める方法は次のJinjaのUNITで扱います。"),
                warning("テンプレートは単なる『ブラウザーへ直接置く静的ファイル』ではありません。サーバーが利用してHTMLを生成します。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("テンプレートはHTMLのひな形です。", "通常templatesフォルダに置きます。", "render_templateでHTMLを生成します。", "RouteがそれをResponseとして返します。", "処理と画面を分けられます。")),
        ],
    },
    "jinja": {
        "objective": "Jinjaの変数表示と簡単な条件分岐を読み、Pythonから渡した値がHTMLに入る仕組みを説明できる。",
        "why": "利用者や教材に応じて同じテンプレートから異なる画面を作るためです。",
        "connection": "前のUNITでは固定のテンプレートを返しました。今回は値を埋め込んで表示を変えます。",
        "sections": [
            section("Pythonから値を渡す",
                code("def index():\n    return render_template('index.html', title='防衛学校')", "関数がtitleという名前で文字列をテンプレートへ渡し、HTMLを返します。", "python"),
                code("<h1>{{ title }}</h1>", "Jinjaの{{ title }}が渡された値に置き換わり、見出しになります。", "html"),
                paragraph("JinjaはFlaskで利用するテンプレートエンジンです。{{ ... }}は値を表示する場所を示します。通常のHTMLテンプレートでは文字列は自動エスケープされ、入力に含まれるタグを安易にHTMLとして実行しないよう助けます。ただし安全性をこれだけに頼り切らないでください。")
            ),
            section("表示するかを選ぶ",
                code("{% if complete %}\n  <p>修了</p>\n{% endif %}", "completeが真ならp要素を生成し、偽なら生成しません。", "html"),
                paragraph("{% ... %}は条件分岐などの制御に使います。ここではifだけ理解すれば十分です。ブラウザーがJinja式を実行するのではなく、サーバー側でHTMLが生成されてから送られます。"),
                warning("{{ title }}をPythonのコード実行欄と考えないでください。サーバー側のテンプレート処理で値をHTMLへ表示する書式です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("Jinjaはテンプレートへ値を埋めます。", "render_templateで値を渡します。", "{{ }}は値を表示します。", "{% if %}で表示条件を指定できます。", "処理はブラウザーではなくサーバー側です。")),
        ],
    },
    "static": {
        "objective": "staticファイルとテンプレートを区別し、CSS・画像・JavaScriptの参照を説明できる。",
        "why": "HTMLだけでなく見た目や画像をブラウザーへ届けるためです。",
        "connection": "テンプレートでHTMLを作りました。CSSなどは別ファイルとして配信できます。",
        "sections": [
            section("静的ファイルの役割",
                paragraph("静的ファイルは通常、要求のたびにテンプレートのような値の埋め込みを行わず配信するCSS、画像、JavaScriptなどです。Flaskでは標準のstaticフォルダに置けます。HTMLテンプレートからそのURLを参照すると、ブラウザーが追加で取得します。"),
                code("<link rel=\"stylesheet\" href=\"{{ url_for('static', filename='style.css') }}\">", "Jinjaのurl_forでstatic内のstyle.cssのURLを作り、ブラウザーにCSSを読み込ませます。", "html"),
                table(["種類", "例", "役割"], [["Template", "lesson.html", "サーバーがHTML生成に利用"], ["Static", "style.css", "ブラウザーへCSSとして配信"]])
            ),
            section("ページが表示されるまで",
                flow("FlaskがテンプレートからHTMLを返す", "ブラウザーがHTMLのlinkを読む", "staticのCSSをRequest", "CSSがHTMLへ適用される"),
                paragraph("JavaScriptや画像もHTMLに参照があれば別のRequestで取得できます。HTMLのResponseが200でも、CSSファイルのURLを間違えると見た目が崩れます。Responseごとに確認することが重要です。"),
                warning("staticへ置いただけでは自動で全ページに反映されません。テンプレート側から参照する必要があります。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("staticにCSS等を置けます。", "テンプレートはHTML生成用です。", "静的ファイルは別のURLで配信されます。", "HTMLから参照して初めて読み込まれます。", "CSSの取得にもHTTP Requestがあります。")),
        ],
    },
    "request_form": {
        "objective": "Flaskのrequest.formから送信値を読み、HTMLのnameとの対応を説明できる。",
        "why": "フォームに入力された回答をサーバー側のPythonで扱うためです。",
        "connection": "第6訓練でformとinputのnameを学びました。今回はFlask側でそれを受け取ります。",
        "sections": [
            section("送信された値を読む",
                code("<form action=\"/answer\" method=\"post\">\n  <input name=\"answer\">\n  <button type=\"submit\">送信</button>\n</form>", "ブラウザーはanswerという名前の値を/answerへPOSTします。", "html"),
                code("from flask import request\n\n@app.route('/answer', methods=['POST'])\ndef answer():\n    value = request.form.get('answer', '')\n    if not value:\n        return '未入力'\n    return '受け取りました'", "request.formからanswerを読みます。ない場合を分け、入力内容をそのままHTMLへ出力しません。", "python"),
                paragraph("requestは現在のHTTP Requestの情報を表します。formはフォームデータの集まりで、HTMLのnameと同じ名前で値を探します。受け取った値は文字列であり、利用者が改変できるため必要な確認を行います。")
            ),
            section("入力を信じ切らない",
                flow("利用者がinputへ入力", "ブラウザーがPOST", "Flaskのrouteが処理", "request.formで値を読む", "必要な確認後に応答"),
                paragraph("このゲームでは選択した番号をそのまま正解と決めず、現在の問題番号や回答済み状態と照合します。ここでは『受け取った値と期待する形を比べる』ことを覚え、詳細なWebセキュリティは第11訓練で扱います。"),
                warning("request.form.getで値を受け取れたことと、その値が正しいことは別です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("inputのnameが送信項目名です。", "requestは現在の要求です。", "request.formでフォーム値を読みます。", "値がない場合も考えます。", "受け取った値は確認が必要です。")),
        ],
    },
    "methods_redirect": {
        "objective": "FlaskのGET/POST分岐とredirectを読み、フォーム送信後に別ページへ移る流れを説明できる。",
        "why": "同じURLで入力画面と送信処理を分け、再読み込み時の重複送信を避ける基本を知るためです。",
        "connection": "request.formでPOSTデータを読みました。次はメソッドごとの処理と応答後の移動です。",
        "sections": [
            section("メソッドごとに処理を選ぶ",
                code("from flask import redirect, request, url_for\n\n@app.route('/login', methods=['GET', 'POST'])\ndef login():\n    if request.method == 'POST':\n        return redirect(url_for('done'))\n    return '入力画面'", "GETなら入力画面、POSTならdoneへ移動するResponseを返します。", "python"),
                paragraph("methodsで受け付けるHTTPメソッドを指定します。request.methodで届いたメソッドを読み、POSTなら送信処理、GETなら画面表示という分け方ができます。例は概念説明で、実際のログイン処理はこの訓練では作りません。"),
                table(["要求", "例の処理"], [["GET /login", "入力画面を返す"], ["POST /login", "doneへのRedirectを返す"]])
            ),
            section("Redirectは次の要求を促す",
                flow("ブラウザーがPOST", "Flaskが処理", "RedirectのResponseを返す", "ブラウザーが移動先へGET"),
                paragraph("redirectはブラウザーに別のURLへ進むよう促す応答です。POSTの後に結果ページへ移ると、元のPOSTを再読み込みで繰り返しにくくなります。ただし重複処理を完全に防ぐ保証はなく、サーバー側の状態確認も必要です。"),
                warning("redirectはPythonの関数内で次の関数を直接呼ぶこととは違います。ブラウザーが新しいRequestを送ります。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("methodsで許可するメソッドを決めます。", "request.methodで届いた方法を読みます。", "GETは主に取得、POSTは送信処理です。", "redirectは移動先へ新しい要求を促します。", "二重送信への対策は別途必要です。")),
        ],
    },
    "session_config": {
        "objective": "Flask session・secret key・環境変数・設定値の役割を説明し、秘密をコードに固定しない理由を理解する。",
        "why": "複数ページにまたがる進捗を扱い、設定や秘密を適切に分けるためです。",
        "connection": "第4訓練でCookieとSessionを学びました。Flaskアプリでの利用を確認します。",
        "sections": [
            section("Sessionと署名",
                paragraph("Flaskのsessionは、複数のRequestにまたがる状態を辞書のように扱えます。標準の方式では署名付きCookieに情報を保存します。署名は改ざん検知に役立ちますが暗号化ではないため、Sessionにパスワードなどの秘密を保存しません。secret keyは署名に必要で、漏れると信頼性が損なわれます。"),
                code("from flask import session\n\nsession['completed'] = True", "sessionへ修了状態を記録する概念例です。別のRequestでも同じブラウザーなら参照できます。", "python"),
                table(["項目", "役割"], [["session", "要求をまたぐ状態"], ["secret key", "署名を支える秘密値"], ["config", "アプリ設定をまとめる仕組み"]])
            ),
            section("設定をコードから分ける",
                paragraph("Flaskのapp.configはアプリの設定値をまとめる場所です。例えば公開して差し支えない表示設定をapp.config['ENABLE_HINTS'] = Trueのように記録できます。環境変数は実行環境から設定値を渡す方法の一つで、秘密値をソースコードへ固定せず環境ごとに値を変えられます。ただし環境変数だけで秘密が自動的に守られるわけではなく、保存場所・権限・ログへの出力にも注意が必要です。"),
                code("import os\n\ndev_enabled = os.environ.get('LEARN_DEV_SHORTCUT') == '1'", "環境変数を読み、明示的に1のときだけ開発用機能を有効にする例です。秘密値を示す例ではありません。", "python"),
                warning("この教材に実際のパスワードやsecret keyを直書きしません。開発用ショートカットも通常環境で有効にしないでください。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("sessionは要求をまたぐ状態です。", "Flask標準のSessionは署名付きCookieを利用します。", "署名は暗号化ではありません。", "secret keyは署名に必要です。", "環境変数は設定をコードから分ける方法の一つです。", "秘密管理には運用上の注意も必要です。")),
        ],
    },
    "testing": {
        "objective": "Flask test clientのGETとstatus_codeを読み、200を確認するテストの意味と限界を説明できる。",
        "why": "変更後にページが壊れていないことを、繰り返し確認できるようにするためです。",
        "connection": "ここまでWebアプリの経路と応答を作りました。最後に自動テストで基本動作を確かめます。",
        "sections": [
            section("ブラウザーなしで要求を試す",
                paragraph("Flaskのtest clientは、テストコードからアプリへHTTP要求を送るための道具です。外部Webサイトへアクセスする必要はありません。status_codeは応答の状態番号で、200はHTTP上の成功を表します。"),
                code("response = client.get('/')\nassert response.status_code == 200", "1行目は/へGETを送ってResponseを保存します。2行目は200であることを検査します。", "python"),
                table(["行", "意味"], [["client.get('/')", "アプリの/へGETする"], ["response.status_code", "返ったHTTP状態番号"], ["assert ... == 200", "期待する成功を確認"]])
            ),
            section("テストで何が分かるか",
                paragraph("200が返れば、その要求に対して成功のResponseがあったと分かります。ただし画面の文章が正しいか、すべてのリンクが動くかまではこの1行だけでは分かりません。必要に応じて表示内容やPOST後の遷移も確認します。既存機能が壊れていないか調べるのが回帰テストです。"),
                flow("コードを変更", "pytestを実行", "失敗した期待値を読む", "原因を調べて修正", "再実行"),
                warning("テストが通ったからといって、すべての使い方が正しいと保証されるわけではありません。テストした範囲を意識します。")
            ),
            section("第2〜7訓練の知識をつなげる",
                flow("ブラウザーでURLを指定", "DNSや経路を使いサーバーへ", "HTTP RequestがFlaskアプリに届く", "RouteがPython関数を選ぶ", "必要ならformデータを読む", "Templateへ値を渡してHTML生成", "HTTP Responseを返す", "ブラウザーがHTMLとstaticのCSS等を表示"),
                paragraph("Pythonの関数・条件分岐と、ネットワーク・HTTP・HTML/CSSがこの一連の流れでつながります。Sessionがあれば要求をまたいで状態を扱えます。テストでは各段階の結果を少しずつ確かめます。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("test clientはアプリへテスト用Requestを送ります。", "HTTP 200は成功の応答です。", "200だけで内容の正しさは保証されません。", "回帰テストは変更による故障を見つけます。", "FlaskのRoute・関数・TemplateがResponseを作ります。", "ブラウザーがstaticも取得して表示します。")),
        ],
    },
}

MORE_EXAMPLES = {
    "framework": section("共通処理と独自処理の境界",
        paragraph("たとえばURLから関数を選ぶ仕組みは、多くのWebアプリで共通します。一方、『回答が正しいか』『どのUNITを解放するか』はこのゲーム固有の規則です。Flaskが経路の土台を提供しても、学習ルールまで自動で作るわけではありません。"),
        paragraph("共通機能に任せる部分と自分で考える部分を分けると、コードが読みやすくなります。問題が起きたときも、ルート登録なのか、アプリの採点ロジックなのか切り分けやすくなります。")
    ),
    "flask": section("アプリオブジェクトを中心に考える",
        paragraph("appは単なる文字列ではなく、ルートや設定を登録していくFlaskアプリのオブジェクトです。後の@app.routeやapp.configは、このappへ情報を結び付けます。変数名を変えること自体は可能ですが、教材ではappで統一します。"),
        paragraph("Flask(__name__)の後に別のrouteを追加すると、同じアプリが受け付けるURLが増えます。どのファイルにルートを書くかは構成次第で、このゲームではLearnのルートを別ファイルに分けています。")
    ),
    "structure": section("変更する場所を探す",
        paragraph("教材の文章が間違っていれば教材データ、表示の見出しやカードが違えばtemplates、余白や色ならstaticのCSS、URLや進捗の動きならPythonのルートを調べます。すべてをapp.pyへ詰めない理由は、役割ごとに原因を追いやすくするためです。"),
        paragraph("ただし細かく分けすぎると、初学者が一つの画面を追うために多くのファイルを行き来することになります。役割がはっきりする程度の分割を目指します。")
    ),
    "route": section("returnを忘れたとき",
        paragraph("ブラウザーへ見せる値は、Flaskがroute関数の返り値から応答へ変換します。関数内でprintを呼んでも、その文字は通常サーバーの出力へ行き、ブラウザーのResponseにはなりません。戻り値を返さないrouteは期待どおりのページを作れません。"),
        paragraph("この違いはPython基礎Ⅱのprintとreturnに直結します。Webアプリでは『サーバーの開発者が見る出力』と『利用者のブラウザーへ返す内容』を明確に分けてください。")
    ),
    "url_route": section("届かない・見つからないを区別する",
        paragraph("ドメイン名からIPを調べられない場合や経路が切れている場合は、Flaskのrouteまで要求が届かない可能性があります。一方、Flaskへ届いたが対応するパスがない場合は、404というHTTP Responseを返せます。画面に『開けない』と見えても、止まった段階は違います。"),
        paragraph("テストで/learn/に200を期待して404が返るなら、URLとroute登録を確認します。通信先へ到達したかの切り分けにHTTPステータスが役立ちます。")
    ),
    "template": section("同じひな形を別の値で使う",
        paragraph("一つのlesson.htmlをUNITごとに複製すると、見た目を直すたびに複数ファイルを修正する必要があります。共通テンプレートへlessonのデータを渡せば、構造は同じまま見出しや本文を変えられます。このゲームもその方式です。"),
        paragraph("テンプレートはPythonの処理を全部置く場所ではありません。採点やロック判定はPython側、結果をどう表示するかはテンプレート側と分けると読みやすくなります。")
    ),
    "jinja": section("値とHTMLの境界",
        paragraph("titleに利用者が入力した文字列が入る場合もあります。Jinjaは通常のHTMLテンプレートで自動エスケープし、<などを文字として表示することでHTMLとして解釈されにくくします。表示のために自動エスケープを無効化する操作は、内容の安全性を理解せずに使わないでください。"),
        paragraph("Jinjaのifで表示を変えても、サーバー側の権限チェックの代わりにはなりません。画面にボタンを隠すことと、そのURLの処理を許可することは別です。")
    ),
    "static": section("追加のRequestを意識する",
        paragraph("HTMLのResponseが成功しても、CSSへのリンク先が間違っていれば見た目は適用されません。ブラウザーはHTMLを読んだ後にCSSのURLへ別のRequestを送るため、問題の場所も分けて確認できます。"),
        paragraph("staticのファイルは、利用者へ配信するためのものです。設定値や秘密情報をstaticへ置けばブラウザーから読める可能性があるため、公開してよいファイルだけを配置します。")
    ),
    "request_form": section("値の名前と内容を確認する",
        paragraph("HTMLの<input name='answer'>から送れば、Flask側はrequest.form.get('answer')で値を探します。nameを別の文字へ変えたのにPython側を直さなければ、期待する値が見つかりません。画面の表示ラベルと送信名は別です。"),
        paragraph("得られた値は文字列として扱うのが基本です。選択肢の番号として使うなら、数字の形か、現在の問題に存在する番号かを確かめます。読み取りと検証を別の手順として考えます。")
    ),
    "methods_redirect": section("POST後の流れを見直す",
        paragraph("回答送信のPOSTを受け、サーバーがsessionの進捗を更新し、redirectで結果URLを返すと、ブラウザーは結果ページへ新たなGETを送ります。これが単にテンプレートを返す場合との違いです。"),
        paragraph("二重POSTが届く可能性は残るため、サーバーは既に回答済みか確認する必要があります。このゲームではsessionの回答状態と問題番号を見て重複加算を防いでいます。")
    ),
    "session_config": section("進捗と設定の寿命",
        paragraph("sessionの進捗はブラウザーとのやり取りに結び付きます。一方、app.configや環境変数の設定はアプリの動き方を決めます。『学習者がどこまで終えたか』と『開発用ボタンを有効にするか』は異なる種類の情報です。"),
        paragraph("この開発版では署名鍵をローカルのGit管理外ファイルに保存して再利用します。同じブラウザーならアプリ再起動後も進捗を読み戻せます。ただしCookieまたは鍵を削除すると読み戻せず、端末間の同期もありません。")
    ),
    "testing": section("テストを一段深くする",
        paragraph("HTTP 200を確認した後、ページに『訓練開始』が含まれるかも確認できます。さらにPOSTを送って正誤と次ページへの遷移を確かめれば、実際の学習フローをより広く検証できます。テストは期待する振る舞いを具体的に書くほど役立ちます。"),
        paragraph("このゲームのpytestは、前の訓練が終わるまで次が開かないことや、BOSSを満点で倒した後に次が解放されることも確かめます。数値200だけで終わらず、目的に沿った条件を検査します。")
    ),
}

for lesson_id, extra in MORE_EXAMPLES.items():
    CHAPTERS[lesson_id]["sections"].insert(-1, extra)
