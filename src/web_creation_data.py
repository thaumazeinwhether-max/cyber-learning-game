"""正式第6訓練の節末問題と総合BOSS。HTML/CSS/JSは読解で確認する。"""

from src.web_creation_chapters import CHAPTERS


def choice(prompt, options, answer, explanation, source=None):
    item = {"prompt": prompt, "options": options, "answer": answer,
            "explanation": explanation}
    if source:
        item["code"] = source
    return item


def truth(prompt, answer, explanation, source=None):
    item = {"type": "true_false", "prompt": prompt, "answer": answer,
            "explanation": explanation}
    if source:
        item["code"] = source
    return item


def term(prompt, answer, explanation, *aliases):
    return {"type": "term", "prompt": prompt, "answer": answer,
            "accepted_answers": [answer, *aliases], "explanation": explanation}


def application(prompt, options, answer, explanation, source=None):
    item = choice(prompt, options, answer, explanation, source)
    item["type"] = "application"
    return item


WEB_CREATION_COURSE = {
    "title": "Web制作基礎訓練",
    "description": "HTMLの構造、CSSの見た目、JavaScriptとDOMの役割をコードから学ぶ正式訓練。",
    "question_mode": "choice",
    "curriculum_number": 6,
    "lesson_label": "UNIT",
    "boss_name": "PAGE STRUCTURE CORE",
    "lessons": [
        {"id": "html", "title": "HTMLとは", "summary": "タグ・要素・属性で文書の意味を表します。", "questions": [
            choice("HTMLが主に担当するのは？", ["文書の内容と構造", "CPUの計算", "ネットワーク間の転送", "データベース更新"], 0, "HTMLはWeb文書の内容と構造を表すマークアップ言語です。"),
            choice("表示される文字はどれ？", ["Hello", "p", "/p", "何もない"], 0, "p要素のタグ間にあるHelloが内容です。", "<p>Hello</p>"),
            choice("hrefの役割は？", ["リンクの移動先", "文字色", "CPUの速度", "段落の個数"], 0, "a要素のhref属性が移動先を示します。", "<a href=\"/learn/\">学習へ</a>"),
            choice("HTMLとPythonの違いとして適切なのは？", ["HTMLは構造を示しPythonは処理を記述できる", "どちらもCSS", "HTMLはOS", "Pythonは画像形式"], 0, "HTMLはマークアップ、Pythonは処理を書くプログラミング言語です。"),
        ]},
        {"id": "document", "title": "HTML文書の基本構造", "summary": "headとbodyなどの位置を読みます。", "questions": [
            choice("ページ本文の見出しを置く場所は？", ["body", "headだけ", "DOCTYPE", "titleだけ"], 0, "主な表示内容はbodyに置きます。"),
            choice("ブラウザーのタブ名などに使われるのは？", ["title", "p", "li", "img"], 0, "titleはheadに置く文書の題名です。"),
            choice("<!DOCTYPE html>の役割は？", ["HTML文書であることを示す", "画像を表示", "フォームを送る", "文字色を変える"], 0, "DOCTYPEは文書型を示します。"),
            choice("h1が入る場所として正しいのは？", ["bodyの内側", "headのtitleの内側", "DOCTYPEの内側", "htmlの外だけ"], 0, "画面で読む見出しはbody内に置きます。", "<html><head><title>題名</title></head><body><h1>本文</h1></body></html>"),
        ]},
        {"id": "text", "title": "見出し・段落", "summary": "文書の階層を意味で表します。", "questions": [
            choice("h2の主な意味は？", ["下位の見出し", "必ず赤い文字", "外部リンク", "フォーム入力"], 0, "h2は見出し階層の一つです。"),
            choice("p要素の意味は？", ["段落", "画像", "表", "ボタン"], 0, "pは文章の段落を表します。"),
            choice("見出しを使う理由として適切なのは？", ["内容の区切りと階層を示す", "必ず文字を最大化するだけ", "送信先を決める", "画像を保存する"], 0, "見出しは文書の構造を表します。"),
            choice("次の構造でUNIT 1に当たるものは？", ["h2", "h1", "p", "CSS"], 0, "h1の下にあるh2が節の見出しです。", "<h1>防衛学校</h1><h2>UNIT 1</h2><p>説明</p>"),
        ]},
        {"id": "media", "title": "リンク・画像・リスト", "summary": "タグと属性を組み合わせて読みます。", "questions": [
            choice("画像ファイルの場所を示す属性は？", ["src", "alt", "href", "name"], 0, "imgのsrcが読み込む画像の場所です。"),
            choice("画像の代替テキストを示す属性は？", ["alt", "src", "method", "color"], 0, "altは画像を見られない場合などに内容や役割を伝えます。"),
            choice("順序を持つ手順に適するのは？", ["olとli", "ulだけ", "imgとsrc", "headとtitle"], 0, "olは順序付きのリスト、liは項目です。"),
            choice("リンク先が/learn/になる要素は？", ["aのhref", "imgのalt", "pの本文", "CSSのcolor"], 0, "a要素のhrefが移動先を指定します。", "<a href=\"/learn/\">一覧へ</a>"),
        ]},
        {"id": "forms", "title": "form", "summary": "フォームからHTTP Requestが作られます。", "questions": [
            choice("formのactionは何を示す？", ["送信先", "文字色", "画像の代替文", "リストの順序"], 0, "actionは送信先のURLパスです。"),
            choice("formのmethod=\"post\"は何を示す？", ["POSTで送信", "GETだけを禁止", "色を変更", "画像を保存"], 0, "methodは送信に使うHTTPメソッドです。"),
            choice("回答ボタンを押した後の基本の流れは？", ["ブラウザーがRequestを作りサーバーが処理", "CSSが回答を採点", "必ずCookieが消える", "HTMLファイルだけでDB更新"], 0, "フォーム送信はHTTP Requestを作ります。"),
            choice("次のフォームの送信先は？", ["/answer", "/learn/", "post", "保存"], 0, "action属性の/answerへ送信します。", "<form action=\"/answer\" method=\"post\"><button type=\"submit\">保存</button></form>"),
        ]},
        {"id": "inputs", "title": "inputとbutton", "summary": "送信データの名前と値を区別します。", "questions": [
            choice("inputのnameが表すのは？", ["送信する項目名", "必ず表示文字", "色", "画像の形式"], 0, "nameはサーバーへ送る値の項目名です。"),
            choice("次の入力欄の送信名は？", ["user_name", "text", "Alice", "input"], 0, "name属性がuser_nameです。", "<input type=\"text\" name=\"user_name\">"),
            choice("フォーム送信に使うボタンは？", ["button type=\"submit\"", "button type=\"button\"だけ", "img", "h1"], 0, "submitボタンでformを送信します。"),
            choice("inputのidとnameについて適切なのは？", ["nameは送信名、idはページ内の目印", "両方とも必ず同じ", "idだけで送信名が決まる", "どちらもCSSの色"], 0, "送信データの識別にはnameを使います。"),
        ]},
        {"id": "css", "title": "CSSとは", "summary": "セレクタ、プロパティ、値を読みます。", "questions": [
            choice("CSSの主な役割は？", ["見た目を指定", "HTTPを転送", "Pythonを実行", "DNSで検索"], 0, "CSSが色や余白など見た目を担当します。"),
            choice("次のbuttonは何？", ["セレクタ", "値", "属性", "関数"], 0, "buttonが対象の要素を選ぶセレクタです。", "button { padding: 12px; }"),
            choice("次の12pxは何？", ["値", "セレクタ", "HTMLタグ", "HTTPコード"], 0, "12pxはpaddingへ設定する値です。", "button { padding: 12px; }"),
            choice("CSSを変えてもHTMLの意味は？", ["同じ要素のまま見た目を変えられる", "必ず別のタグになる", "フォームが消える", "サーバーが不要になる"], 0, "構造はHTML、見た目はCSSが主に扱います。"),
        ]},
        {"id": "css_layout", "title": "CSS基礎", "summary": "色・余白・幅・表示方式を読みます。", "questions": [
            choice("境界線の内側の余白は？", ["padding", "margin", "color", "display"], 0, "paddingは内容と境界の間の余白です。"),
            choice("要素の外側の余白は？", ["margin", "padding", "font-size", "border"], 0, "marginは要素の外側の余白です。"),
            choice("次のfont-sizeは何を変える？", ["文字の大きさ", "画像の場所", "送信メソッド", "プロセス数"], 0, "font-sizeは文字の大きさを指定します。", "h1 { font-size: 24px; }"),
            choice("borderとwidthの組み合わせで正しいのは？", ["境界線と幅", "文字色と背景色", "送信先と値", "見出しと段落"], 0, "borderは境界線、widthは幅です。"),
        ]},
        {"id": "javascript", "title": "JavaScriptの役割", "summary": "クリックなどのイベントへ反応します。", "questions": [
            choice("JavaScriptの主な用途は？", ["操作への反応や動き", "HTMLの文書型だけ", "CSSの余白だけ", "ルーターの転送だけ"], 0, "JavaScriptはブラウザーでの振る舞いを追加できます。"),
            choice("clickイベントはいつ起こる？", ["利用者がクリックしたとき", "HTMLを保存したときだけ", "DNSが動いたとき", "電源を切ったとき"], 0, "クリックという操作に反応するイベントです。"),
            choice("次のコードは何を登録する？", ["ボタンを押すとHelloを表示", "ページを開くたび必ずHelloを表示", "CSSを消す", "フォームを自動送信"], 0, "click時にalertを実行する処理を登録しています。", "button.addEventListener('click', function () { alert('Hello'); });"),
            choice("JavaScriptなしでHTMLフォーム送信は可能？", ["可能", "絶対に不可能", "CSS次第", "DNS次第"], 0, "formとsubmitだけでもRequestを送れます。"),
        ]},
        {"id": "dom", "title": "DOMと入力・画面表示", "summary": "要素を探し、入力を読んで表示を更新します。", "questions": [
            choice("DOMの説明として適切なのは？", ["ブラウザーがHTMLを扱うための文書構造", "CPUの型番", "HTTPのステータス", "画像形式"], 0, "DOMはブラウザーが文書の要素を扱うための表現です。"),
            choice("getElementById('message')が探すものは？", ["idがmessageの要素", "nameが必ずmessageのフォーム", "すべての画像", "すべてのサーバー"], 0, "指定したidの要素を取得します。"),
            choice("inputに入力された現在の文字を読むプロパティは？", ["value", "src", "href", "method"], 0, "inputのvalueが現在の入力値です。"),
            choice("次の代入が主に変えるものは？", ["画面内の文字", "サーバーのDB", "DNS設定", "HTTPメソッド"], 0, "textContentの変更はDOM上の文字表示を変えます。", "document.getElementById('message').textContent = '開始';"),
        ]},
    ],
    "boss": [
        truth("HTMLは主にWeb文書の意味と構造を表し、CSSは見た目を指定する。", "true", "内容の構造と見た目は役割が異なります。"),
        application("次のコードでタブ名と本文見出しの組み合わせは？", ["SampleとHello", "HelloとSample", "両方Sample", "両方Hello"], 0, "titleはタブ名、body内のh1が本文見出しです。", "<head><title>Sample</title></head><body><h1>Hello</h1></body>"),
        term("画像の代替テキストに使う属性は？", "alt", "imgのalt属性が代替説明です。"),
        application("手順1→2→3を表すなら適切な組み合わせは？", ["olとli", "ulだけ", "imgとalt", "aとhrefだけ"], 0, "順序のあるリストはolで、項目はliです。"),
        truth("formのmethod='post'は送信内容が自動的に暗号化されることを意味する。", "false", "POSTはメソッドです。通信保護にはHTTPS等が必要です。"),
        application("次のフォームでサーバーに送る項目名は？", ["answer", "text", "POST", "送信"], 0, "inputのname属性が送信データの項目名です。", "<form method=\"post\"><input type=\"text\" name=\"answer\"><button type=\"submit\">送信</button></form>"),
        term("CSSで対象要素を指定するbuttonなどの部分を何という？", "セレクタ", "セレクタがCSS規則の適用先を選びます。", "selector"),
        application("次のCSSが指定するのは？", ["ボタン内側の余白を12px", "ボタン外側の余白を12px", "文字色を12px", "送信先を12px"], 0, "paddingは境界の内側の余白です。", "button { padding: 12px; }"),
        truth("h1の文字をCSSで小さくしても、HTML上は見出し要素のままである。", "true", "見た目の大きさと要素の意味は別です。"),
        application("次のJavaScriptが動くのはいつ？", ["ボタンのclick時", "HTMLを保存した瞬間", "CSSの読込時", "DNS問い合わせ時"], 0, "addEventListenerがclick時の処理を登録します。", "button.addEventListener('click', function () { alert('Hello'); });"),
        term("ブラウザーがHTML要素をプログラムから扱えるようにした文書構造の略称は？", "DOM", "Document Object Modelの略で、要素を取得・更新できます。"),
        application("画面のinputを読み、サーバーへ送らずpの文字だけ変えたい。適切なのは？", ["valueを読みtextContentを更新", "actionをPOSTにして保存だけ", "DNSを変更", "CSSのmarginを変更"], 0, "入力値を読みDOMの文字を更新すれば画面だけが変わります。"),
        application("フォーム送信でFlaskへ値が届く流れは？", ["inputのnameと値→formがRequest→サーバーが処理", "CSS→CPU→Cookieだけ", "DOM更新だけで必ず保存", "alt→src→DNS"], 0, "HTMLフォームがHTTP Requestを作り、サーバーの処理へ渡します。"),
        application("ページの構造・見た目・クリック後の表示変更の担当順は？", ["HTML・CSS・JavaScript", "CSS・HTML・DNS", "HTTP・Cookie・IP", "JavaScript・CPU・HTML"], 0, "三者は異なる役割を持ち連携します。"),
    ],
}

for lesson in WEB_CREATION_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])

# 固定問題順のまま、正解番号が一つに偏らないよう表示順を分散する。
for lesson_number, lesson in enumerate(WEB_CREATION_COURSE["lessons"]):
    for question_number, question in enumerate(lesson["questions"]):
        offset = (lesson_number + question_number) % 4
        question["options"] = question["options"][offset:] + question["options"][:offset]
        question["answer"] = (question["answer"] - offset) % 4
for question_number, question in enumerate(WEB_CREATION_COURSE["boss"]):
    if "options" in question:
        offset = question_number % 4
        question["options"] = question["options"][offset:] + question["options"][:offset]
        question["answer"] = (question["answer"] - offset) % 4

for question in (
    [item for lesson in WEB_CREATION_COURSE["lessons"] for item in lesson["questions"]]
    + WEB_CREATION_COURSE["boss"]
):
    if "options" in question:
        correct_option = question["options"][question["answer"]]
        question["wrong_explanations"] = {
            str(index): f"「{option}」では、ここで求める「{correct_option}」の役割・結果を表せません。{question['explanation']}"
            for index, option in enumerate(question["options"])
            if index != question["answer"]
        }
