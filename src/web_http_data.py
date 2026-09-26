"""正式第4訓練。Webの要求・応答を章末まで通して確認する。"""

from src.web_http_chapters import CHAPTERS
from src.choice_order import arrange_choices


def choice(prompt, options, answer, explanation):
    return {"prompt": prompt, "options": options, "answer": answer,
            "explanation": explanation, "hint": explanation}


def truth(prompt, answer, explanation):
    return {"type": "true_false", "prompt": prompt, "answer": answer,
            "explanation": explanation, "hint": explanation}


def term(prompt, answer, explanation, *aliases):
    return {"type": "term", "prompt": prompt, "answer": answer,
            "accepted_answers": [answer, *aliases], "explanation": explanation,
            "hint": explanation}


def application(prompt, options, answer, explanation):
    item = choice(prompt, options, answer, explanation)
    item["type"] = "application"
    return item


WEB_HTTP_COURSE = {
    "title": "Web・HTTP基礎訓練",
    "description": "URLからHTTP、状態管理、画面表示までWebの一往復を理解します。",
    "question_mode": "choice",
    "curriculum_number": 4,
    "lesson_label": "UNIT",
    "boss_name": "WEB PROTOCOL CORE",
    "lessons": [
        {"id": "web", "title": "Webとクライアント・サーバー", "summary": "Webと通信基盤、依頼側と応答側を分けます。", "questions": [
            choice("Webとインターネットの関係は？", ["Webはインターネットなどを利用する仕組み", "完全に同じ意味", "インターネットはブラウザー一台", "WebはCPUの別名"], 0, "インターネットは通信基盤で、Webはその上で情報を扱います。"),
            choice("ページを要求するブラウザーの役割は？", ["クライアント", "サーバーだけ", "ルーター", "DNS"], 0, "要求を送る側がクライアントです。"),
            choice("要求を受けてページのデータを返す側は？", ["サーバー", "キーボード", "CSS", "ポート番号"], 0, "サーバーが要求を処理して応答します。"),
            choice("同じPCが場面によって依頼側にも応答側にもなれる？", ["なれる", "絶対になれない", "OSなしならなれる", "URLだけが決める"], 0, "クライアントとサーバーは通信中の役割です。"),
        ]},
        {"id": "url", "title": "URL・ドメイン", "summary": "場所を表す文字列と名前解決を学びます。", "questions": [
            choice("https://example.com/learn/ のexample.comは？", ["ホスト名", "HTTP本文", "ステータスコード", "CSS"], 0, "example.comは通信先を示すホスト名です。"),
            choice("URLの/learn/部分は？", ["パス", "IPv4アドレス", "Cookie", "RAM"], 0, "パスはサーバーへ要求する場所を表します。"),
            choice("ドメイン名からIP情報を調べる仕組みは？", ["DNS", "CSS", "POST", "HTML"], 0, "DNSが名前に対応する情報を調べます。"),
            choice("URLパスについて正しい説明は？", ["必ずPC上の物理ファイル名", "Webアプリの処理対象にもなり得る", "必ずIPアドレス", "必ずCookie"], 1, "URLパスはサーバー側のルート等に対応する場合もあります。"),
        ]},
        {"id": "http", "title": "HTTPの基本", "summary": "Web上の要求と応答の約束を学びます。", "questions": [
            choice("HTTPの役割は？", ["Webの要求と応答の約束", "CPUの命令セット", "画像形式", "OSの種類"], 0, "HTTPはクライアントとサーバーの要求・応答を定めます。"),
            choice("HTTP Requestを送る典型的な側は？", ["ブラウザー", "ストレージ", "ディスプレイ", "プリンター"], 0, "ブラウザーなどのクライアントがRequestを送ります。"),
            choice("HTTP Responseを返す側は？", ["サーバー", "キーボード", "拡張子", "RAMだけ"], 0, "サーバーが要求を処理してResponseを返します。"),
            choice("HTTPSについて適切なのは？", ["TLSでHTTP通信を保護する", "サイトの内容を必ず正しいと保証", "HTTPと無関係", "HTMLの別名"], 0, "HTTPSはTLSで通信を保護しますが、内容の真実性を保証するものではありません。"),
        ]},
        {"id": "request", "title": "HTTP Request", "summary": "メソッド・パス・ヘッダー・ボディを読みます。", "questions": [
            choice("Requestのメソッドが表すのは？", ["要求する操作の種類", "画面の色", "CPUの温度", "画像のサイズだけ"], 0, "GETやPOSTなどが操作の種類を表します。"),
            choice("POST /answer の/answerは何を表す？", ["要求対象のパス", "ステータスコード", "Cookieの有効期限", "RAM容量"], 0, "パスはサーバー上で要求する対象です。"),
            choice("Content-Typeのような付加情報が入るのは？", ["ヘッダー", "CPU", "ディスプレイ", "拡張子"], 0, "ヘッダーに本文の種類などの付加情報を載せます。"),
            choice("フォームのanswer=2を送るデータ本体に当たる部分は？", ["ボディ", "ステータス", "IPアドレス", "URLのスキーム"], 0, "Requestのボディに送信データ本体を載せられます。"),
        ]},
        {"id": "response", "title": "HTTP Response", "summary": "結果番号と返される本文を読みます。", "questions": [
            choice("Responseのステータスコードは？", ["処理結果の分類", "要求するメソッド", "キーボード入力", "ファイル名だけ"], 0, "ステータスコードが応答の結果を示します。"),
            choice("HTTP 200の基本的な意味は？", ["要求が成功", "必ずページは存在しない", "必ずサーバー停止", "転送だけ"], 0, "200は成功を表す代表的なコードです。"),
            choice("ResponseのHTML本文が入るのは？", ["ボディ", "メソッド", "IPアドレス", "DNS"], 0, "ボディは返すデータ本体です。"),
            choice("HTMLが返った後、ブラウザーは？", ["CSSや画像を追加で要求し得る", "絶対に通信しない", "CPUを破棄する", "URLを必ず変更する"], 0, "ページ表示に必要な追加資源を要求する場合があります。"),
        ]},
        {"id": "methods", "title": "GETとPOST", "summary": "取得とデータ送信の使い分けを学びます。", "questions": [
            choice("教材ページを取得する要求に一般的なのは？", ["GET", "POSTのみ", "404", "CSS"], 0, "GETは情報の取得に使われます。"),
            choice("回答フォームを送って処理を依頼するのに一般的なのは？", ["POST", "200", "HTML", "DNS"], 0, "POSTはデータを送って処理を依頼するときによく使います。"),
            choice("POSTを使えば内容は自動的に暗号化される？", ["される", "されない。HTTPS等が必要", "CSSが暗号化する", "URLパスが暗号化する"], 1, "POSTだけでは暗号化されません。通信保護にはHTTPS等が必要です。"),
            choice("GETの用途として望ましいのは？", ["原則として状態を変えない情報取得", "常に削除操作", "必ず秘密情報送信", "コードの実行だけ"], 0, "GETは原則として状態を変えない取得に使います。"),
        ]},
        {"id": "status", "title": "HTTPステータスコード", "summary": "200・3xx・4xx・5xxを読み分けます。", "questions": [
            choice("404が属する分類は？", ["4xx", "2xx", "3xx", "5xx"], 0, "404は4xxで、要求した資源が見つからないことを示します。"),
            choice("500が属する分類は？", ["5xx", "2xx", "3xx", "4xx"], 0, "500は5xxで、サーバー側の処理失敗です。"),
            choice("転送などを示す分類は？", ["3xx", "2xx", "4xx", "5xx"], 0, "3xxは転送などを示します。"),
            choice("200が返った場合に分かることは？", ["応答上は成功。内容の正しさは別途確認", "教材が必ず正しい", "サーバーが必ず停止", "利用者が必ずログイン"], 0, "200はHTTP上の成功ですが、画面内容の品質までは保証しません。"),
        ]},
        {"id": "message", "title": "HeaderとBody", "summary": "付加情報とデータ本体を区別します。", "questions": [
            choice("Content-Typeが入るのは？", ["Header", "Bodyだけ", "IPアドレス", "DNS"], 0, "Content-Typeは本文の種類を示すヘッダーです。"),
            choice("<h1>Hello</h1>という返答の本文は？", ["Body", "Header", "ステータスだけ", "ポート番号"], 0, "返すHTMLデータ本体はBodyです。"),
            choice("HeaderとBodyが使われる場所は？", ["RequestとResponseの両方", "Responseだけ", "Requestだけ", "画面だけ"], 0, "両方のHTTPメッセージにヘッダーがあり、必要に応じてボディがあります。"),
            choice("HTTPメッセージは必ず長いBodyを持つ？", ["持つ", "必要がなければBodyがない場合もある", "Headerを持てない", "ステータスを持てない"], 1, "ボディは必要なときに利用します。"),
        ]},
        {"id": "state", "title": "CookieとSession", "summary": "複数の要求にまたがる状態を学びます。", "questions": [
            choice("Cookieの基本的な保存場所は？", ["ブラウザー側", "CPU内だけ", "必ず紙", "URLパスだけ"], 0, "Cookieはブラウザー側に保存され、後の要求で送られます。"),
            choice("Sessionの目的は？", ["複数要求の状態を結び付ける", "IPアドレスを作る", "CSSを描く", "CPUを交換する"], 0, "Sessionは一連の要求にまたがる状態を扱います。"),
            choice("Flaskの署名付きCookie型Sessionの署名は何を助ける？", ["改ざん検知", "内容の暗号化", "速度測定", "画像変換"], 0, "署名は改ざん検知に役立ちますが、暗号化ではありません。"),
            choice("別ブラウザーにした場合、このゲームの進捗は？", ["自動同期とは限らない", "必ず共有される", "OSが消える", "CookieがCPUになる"], 0, "ログインなしでブラウザーごとのCookieに依存するため自動共有されません。"),
        ]},
        {"id": "page", "title": "画面表示までの流れ", "summary": "HTML・CSS・JavaScriptを通信の流れへつなぎます。", "questions": [
            choice("HTMLの主な役割は？", ["内容と構造", "ネットワーク間の転送", "IPの配布", "長期保存"], 0, "HTMLは見出しや段落など内容と構造を表します。"),
            choice("CSSの主な役割は？", ["見た目や配置", "HTTPステータスの決定", "DNSの名前解決", "OSの起動"], 0, "CSSは色、余白、配置など見た目を扱います。"),
            choice("JavaScriptの主な役割として適切なのは？", ["ブラウザーでの動きや操作への反応", "ネットワーク間のルーティング", "IPの物理製造", "必ずDBの保存"], 0, "JavaScriptは画面の動きや操作への反応を担えます。"),
            choice("URL入力から画面表示の流れは？", ["DNS→HTTP要求・応答→ブラウザーがHTML等を解釈", "CSS→CPU廃棄→表示", "Cookieだけで表示", "ステータスだけでHTML生成"], 0, "名前解決、要求・応答、受信した内容の解釈がつながります。"),
        ]},
    ],
    "boss": [
        truth("Webはインターネットを使う仕組みの一つで、インターネット上のすべての通信がWebとは限らない。", "true", "Webと通信基盤は異なります。"),
        term("Webでクライアントとサーバーが要求・応答を行うためのプロトコルの略称は？", "HTTP", "HTTPがWeb上の要求・応答を定めます。"),
        application("https://example.com/learn/ のホスト名とパスの組み合わせは？", ["example.com と /learn/", "https と example.com", "/learn/ と https", "200 と /learn/"], 0, "example.comがホスト名、/learn/がパスです。"),
        truth("ブラウザーがHTTP Requestを送り、サーバーがHTTP Responseを返す。", "true", "要求と応答の方向を区別します。"),
        term("HTTP Responseで処理結果を3桁の数で示すものは？", "ステータスコード", "200や404などのステータスコードで結果を分類します。", "status code", "HTTPステータスコード"),
        application("教材ページは表示できず404が返った。まず読み取れることは？", ["要求した資源が見つからない", "必ずDB故障", "必ずDNS不通", "要求は完全成功"], 0, "404は要求した資源が見つからないことを示します。"),
        truth("POSTを使えばHTTPSがなくても送信内容が自動的に暗号化される。", "false", "POSTはメソッドであり暗号化の仕組みではありません。"),
        application("回答を送る要求のメソッド・データ本体として適切なのは？", ["POSTとRequest Body", "200とResponse Header", "CSSとIP", "404とDNS"], 0, "回答送信にはPOSTを使い、データ本体はRequest Bodyに載せられます。"),
        term("HTTPでContent-Typeのような付加情報を置く部分は？", "Header", "Headerはメッセージの扱い方を伝えます。", "ヘッダー"),
        truth("Cookieはブラウザー側に保存され得るが、Sessionの実装方法は一つに固定されない。", "true", "Sessionにはサーバー側保持や署名付きCookie利用など複数の実装があります。"),
        application("サーバーがHTMLを200で返した後、ブラウザーがCSSを追加取得する理由は？", ["HTMLの構造に見た目の指定を適用するため", "200が必ずエラーだから", "DNSを消すため", "CPUを再起動するため"], 0, "HTMLとCSSは役割が異なり、必要な資源を追加取得します。"),
        application("URLを開きログイン状態を引き継ぐ流れとして適切なのは？", ["DNS等で宛先へ向かい、HTTP要求にCookieを含め、Sessionの状態を参照する", "CookieだけでDNS・HTTPが不要", "CSSが認証を決定", "IPがログイン情報そのもの"], 0, "通信先への接続、HTTP、状態管理が連携します。"),
        application("ブラウザーがページを表示するまでの順序として適切なのは？", ["URL→名前解決→HTTP Request→Response→HTML/CSS等の解釈", "Response→URL→DNS不要→表示", "CSS→ステータス→URL", "Cookie→CPU交換→画面"], 0, "名前解決とHTTPのやり取りを経てブラウザーが内容を描画します。"),
        application("学習ゲームで回答をPOSTし、結果ページを表示する説明として適切なのは？", ["Request Bodyの回答をサーバーが処理し、Responseを返し、Sessionで進捗をつなぐ", "POSTだけで暗号化・採点・表示がすべて保証される", "CookieがCPU命令を実行する", "HTMLがルーターを制御する"], 0, "メソッド、ボディ、サーバー処理、応答、Sessionが別の役割を担います。"),
    ],
}

for lesson in WEB_HTTP_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])

arrange_choices(WEB_HTTP_COURSE)
