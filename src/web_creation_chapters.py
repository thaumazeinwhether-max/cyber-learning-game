"""正式第6訓練「Web制作基礎」の参考書型教材。"""

from src.chapter_blocks import code, flow, key_points, note, paragraph, section, table, warning


CHAPTERS = {
    "html": {
        "objective": "HTMLのタグ・要素・属性を区別し、ページの内容と構造を表す役割を説明できる。",
        "why": "Flaskが返すHTMLを読めるようになるための最初の一歩です。",
        "connection": "第4訓練ではResponseのHTMLをブラウザーが受け取ると学びました。今回はその中身を読みます。",
        "sections": [
            section("HTMLは内容の印付け",
                paragraph("HTMLはHyperText Markup Languageの略で、Web文書の内容と構造を表すマークアップ言語です。計算手順を記述するPythonとは役割が違います。タグで文章の意味や構造を示し、ブラウザーはそれを解釈します。"),
                code("<p>Hello</p>", "開始タグ<p>、内容Hello、終了タグ</p>で一つの段落要素を表します。", "html"),
                table(["語", "意味"], [["タグ", "<p>のような印"], ["要素", "タグと内容を含む文書の一部分"], ["属性", "開始タグへ追加する情報"]])
            ),
            section("属性で追加情報を渡す",
                paragraph("属性は開始タグに名前と値を書く追加情報です。例えばリンクのhrefは移動先を示します。すべての要素に同じ属性が使えるわけではなく、要素の目的に応じて選びます。HTMLはページの構造を作り、色や余白は主にCSSが担当します。"),
                code("<a href=\"/learn/\">学習へ</a>", "a要素がリンク、href属性が移動先、タグの間の文字が表示内容です。", "html"),
                warning("HTMLを『Webページを作るプログラミング言語』と覚えると、構造と処理の違いが曖昧になります。ここでは文書を意味付ける言語です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("HTMLはWeb文書の内容と構造を表します。", "タグは内容の意味を示す印です。", "要素はタグと内容などのまとまりです。", "属性は開始タグに付ける追加情報です。", "PythonやJavaScriptと役割が異なります。")),
        ],
    },
    "document": {
        "objective": "DOCTYPE・html・head・title・bodyの役割を説明し、最小のHTML文書を読める。",
        "why": "一部のタグだけでなく、文書全体のどこに何を書くか理解するためです。",
        "connection": "前のUNITで一つの要素を学びました。今度は複数の要素で一つの文書を構成します。",
        "sections": [
            section("文書の骨組み",
                code("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n  <title>Sample</title>\n</head>\n<body>\n  <h1>Hello</h1>\n</body>\n</html>", "DOCTYPEはHTML文書であることを示し、htmlが全体、headに設定情報、bodyに主な表示内容を置きます。", "html"),
                paragraph("headはページの題名や付加情報などを置く部分です。titleの文字は通常ブラウザーのタブ名などに使われ、bodyのh1のようにページ本文へ大きく表示されるわけではありません。bodyには利用者が読む見出しや段落などを置きます。"),
                table(["部分", "主な役割"], [["<!DOCTYPE html>", "文書型を示す"], ["html", "文書全体"], ["head / title", "設定情報と題名"], ["body", "主な表示内容"]])
            ),
            section("入れ子と終了タグ",
                paragraph("上の例ではtitleはheadの内側、h1はbodyの内側にあります。このように要素を入れ子にして階層を作ります。対応する終了タグを意識しないと、意図しない範囲まで含めてしまいます。インデントは読みやすさのためですが、構造を確認する助けになります。"),
                flow("ブラウザーがHTMLを受け取る", "文書の要素と階層を読む", "headの情報を扱う", "bodyの内容を画面に表示"),
                warning("titleとh1を同じものと考えないでください。どちらも題名に関わりますが、文書中での置き場所と主な表示先が違います。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("DOCTYPEはHTML文書であることを示します。", "htmlが文書全体を囲みます。", "headには設定情報を置きます。", "titleはタブ名などに使われます。", "bodyが主なページ内容です。", "要素は入れ子の階層を作ります。")),
        ],
    },
    "text": {
        "objective": "h1〜h6とpを使って見出しと段落の階層を説明できる。",
        "why": "文章を見た目だけでなく意味のある構造として伝えるためです。",
        "connection": "文書のbodyに入れる内容として、まず見出しと段落を扱います。",
        "sections": [
            section("見出しは文章の構造",
                paragraph("h1〜h6は見出しの段階を表します。数字が小さいほど上位の見出しです。pは段落を表します。見出しを使う理由は単に字を大きくするためではなく、文章のまとまりと階層を表すためです。見た目の大きさはCSSで調整できます。"),
                code("<h1>防衛学校</h1>\n<h2>UNIT 1</h2>\n<p>コンピュータの基本を学びます。</p>", "h1が全体の見出し、h2がその下の節、pが説明文です。", "html"),
                table(["要素", "意味"], [["h1", "上位の見出し"], ["h2〜h6", "段階的な下位の見出し"], ["p", "文章の段落"]])
            ),
            section("意味と見た目を分ける",
                paragraph("本文をすべてh1にすると大きくは見えても構造が分かりにくくなります。逆に、CSSでpの文字を大きくしても、要素の意味は段落のままです。見出しの順序が自然なら、読者も支援技術も内容の区切りを追いやすくなります。"),
                note("確認例", "この教材のUNIT名は上位の見出し、各説明節は下位の見出し、説明は段落です。"),
                warning("h1〜h6を『文字サイズを選ぶタグ』としてだけ使わないでください。文書の意味上の階層です。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("h1〜h6は見出しの階層です。", "pは段落です。", "見出しは内容の区切りを示します。", "見た目はCSSで調整できます。", "意味のある順序で使います。")),
        ],
    },
    "media": {
        "objective": "リンク・画像・順序付き/なしリストを読み、タグと属性の役割を区別できる。",
        "why": "文章以外の情報をページへ配置し、別ページへ移動できるようにするためです。",
        "connection": "見出しと段落で文章を組み立てました。次は移動先、画像、項目のまとまりです。",
        "sections": [
            section("リンクと画像",
                paragraph("a要素はリンクで、href属性に移動先を書きます。img要素は画像で、src属性が画像の場所、alt属性が画像の代替テキストです。altは画像を見られない状況でも内容や役割を伝えるために重要です。画像が装飾のみの場合は用途に合う扱いを考えます。"),
                code("<a href=\"/learn/\">訓練一覧</a>\n<img src=\"/static/map.png\" alt=\"訓練の進行図\">", "1行目のhrefは移動先、2行目のsrcは画像の場所、altは代替説明です。", "html"),
                table(["要素/属性", "役割"], [["a / href", "リンクと移動先"], ["img / src", "画像と読み込み先"], ["img / alt", "画像の代替テキスト"]])
            ),
            section("まとまった項目を示す",
                paragraph("ulは順序を重視しないリスト、olは順序が意味を持つリストです。項目はliで書きます。手順の1、2、3にはol、並列の学習項目にはulが自然です。見た目の記号だけでなく内容の意味で選びます。"),
                code("<ol>\n  <li>教材を読む</li>\n  <li>問題に答える</li>\n</ol>", "olで順序を持つ手順を作り、liで各項目を表します。", "html"),
                warning("hrefとsrcはどちらも場所を示しますが、aの移動先とimgの画像読み込み先で使い方が違います。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("aとhrefはリンクを作ります。", "imgとsrcは画像を指定します。", "altは画像の代替説明です。", "ulは順序を重視しないリストです。", "olは順序付きリストです。", "liが個々の項目です。")),
        ],
    },
    "forms": {
        "objective": "formのactionとmethodを読み、入力がHTTP Requestとして送られる流れを説明できる。",
        "why": "学習ゲームの回答送信やFlaskへの入力が、画面上だけで終わらないことを理解するためです。",
        "connection": "第4訓練ではGETとPOSTを学びました。HTMLのformはそれらの要求を作る入口です。",
        "sections": [
            section("formは送信のまとまり",
                paragraph("form要素は利用者からの入力をまとめて送信します。actionには送信先のURLパス、methodにはHTTPメソッドを指定します。ボタンを押すとブラウザーがフォームの値からRequestを作り、サーバーが受け取って処理します。"),
                code("<form action=\"/answer\" method=\"post\">\n  <input name=\"choice\">\n  <button type=\"submit\">回答</button>\n</form>", "formが送信先とPOSTを指定し、inputの値を送信ボタンで送ります。", "html"),
                flow("inputへ入力", "submitボタンを押す", "ブラウザーがPOST Requestを作る", "サーバーが/answerで処理", "Responseが返る")
            ),
            section("GET/POSTとの接続",
                paragraph("検索のような取得はGET、回答や登録などの処理依頼はPOSTがよく使われます。methodを書かなければGETが既定ですが、意図が伝わるように明示する方が読みやすい場合があります。送った値は常に正しいとは限らないので、サーバー側で確認します。"),
                table(["属性", "例", "役割"], [["action", "/answer", "送信先"], ["method", "post", "要求方法"]]),
                warning("formがあるだけで入力が保存されるわけではありません。送信先のサーバーに対応する処理が必要です。POSTは暗号化そのものでもありません。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("formは入力をまとめて送信します。", "actionは送信先です。", "methodはGET/POSTなどです。", "submitでRequestが作られます。", "処理はサーバー側にも必要です。")),
        ],
    },
    "inputs": {
        "objective": "inputのtype・nameとbuttonのtypeを読み、サーバーへ送られる名前と値の関係を説明できる。",
        "why": "フォームでどの入力が何という名前で届くか理解するためです。",
        "connection": "formの送信先を学びました。今回はその中に置く個々の入力を見ます。",
        "sections": [
            section("値に名前を付けて送る",
                paragraph("inputは入力欄を作ります。typeは入力の種類を指定し、textなら一行の文字入力です。nameは送信時の項目名になります。利用者がAliceと入力すると、サーバーはnameという名前に対応するAliceという値を受け取れます。"),
                code("<form action=\"/save\" method=\"post\">\n  <input type=\"text\" name=\"name\">\n  <button type=\"submit\">保存</button>\n</form>", "inputのtypeが入力形式、nameが送信する項目名。buttonのsubmitでフォームを送ります。", "html"),
                table(["部分", "役割"], [["type=\"text\"", "文字入力欄"], ["name=\"name\"", "送る値の項目名"], ["button type=\"submit\"", "フォーム送信"]])
            ),
            section("画面表示と送信データを分ける",
                paragraph("ボタンに見える『保存』は表示文です。サーバーへ送る入力の識別にはinputのnameが使われます。nameがない入力は通常フォームの送信データに含まれません。どの値が送られるかは、入力の種類や状態にもよります。"),
                note("確認例", "このゲームの回答画面は選択肢にanswerというnameを付け、サーバーがその値を読みます。"),
                warning("id属性は画面内で要素を特定する用途がありますが、送信データの項目名はnameです。二つを混同しないでください。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("inputは入力欄です。", "typeは入力の種類です。", "nameは送信データの項目名です。", "submitボタンでフォームを送れます。", "表示文字と送信名は別です。")),
        ],
    },
    "css": {
        "objective": "CSSのセレクタ・プロパティ・値を読み、HTMLの構造と見た目の役割を分けて説明できる。",
        "why": "ページの内容を保ちながら、読みやすい色や余白をまとめて指定するためです。",
        "connection": "HTMLでフォームまでの構造を作りました。CSSはその構造の見た目を調整します。",
        "sections": [
            section("CSSの規則",
                paragraph("CSSはCascading Style Sheetsの略で、HTMLなどの見た目を指定します。セレクタで対象を選び、波括弧内にプロパティ: 値を書きます。HTMLのタグ名を変えずに、文字色や余白を変えられます。"),
                code("button {\n    padding: 12px;\n    color: white;\n}", "buttonが対象、paddingとcolorがプロパティ、12pxとwhiteが値です。", "css"),
                table(["部分", "役割"], [["button", "セレクタ：対象の要素"], ["padding", "プロパティ：内側の余白"], ["12px", "値：余白の大きさ"]])
            ),
            section("構造と見た目を分担",
                paragraph("同じbuttonというHTML要素にも、CSSで色や余白を付けられます。HTMLを『青くするためのタグ』に変えるのではなく、意味のある要素を選んで見た目を指定します。複数の規則が重なったときの優先順を扱う仕組みが名前のCascadingに含まれますが、詳細は後で学べます。"),
                note("具体例", "この教材のカードやコード枠はHTMLで構造を作り、CSSが背景や余白を整えています。"),
                warning("CSSはサーバーへ回答を送る処理を担当しません。動きと通信は別の仕組みです。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("CSSは見た目を指定します。", "セレクタが対象を選びます。", "プロパティと値で色や余白を決めます。", "HTMLの意味とCSSの見た目は別です。", "同じ要素へ複数の規則が関わる場合があります。")),
        ],
    },
    "css_layout": {
        "objective": "色・文字・margin・padding・border・width・displayの基本を読み、余白の内外を区別できる。",
        "why": "読みにくい画面を、内容の意味を変えずに整えるためです。",
        "connection": "前のUNITでCSSの書式を学びました。今回はよく使うプロパティを場面ごとに整理します。",
        "sections": [
            section("文字と色",
                paragraph("colorは文字色、background-colorは背景色、font-sizeは文字の大きさです。値には色名や長さを使えます。見やすさには背景とのコントラストも重要です。色だけで正誤を伝えると、読みにくい利用者がいるため、文字でも状態を示します。"),
                code(".notice {\n    color: navy;\n    background-color: white;\n    font-size: 18px;\n}", ".noticeの要素に文字色・背景色・文字サイズを指定します。", "css"),
                table(["プロパティ", "意味"], [["margin", "要素の外側の余白"], ["padding", "境界の内側の余白"], ["border", "境界線"], ["width", "幅"], ["display", "要素の表示方式"]])
            ),
            section("余白と基本レイアウト",
                paragraph("marginは要素の外側、paddingは内容と境界の間の余白です。borderはその境界線です。widthで幅を指定できますが、画面が狭い場合に固定幅がはみ出さないか注意します。displayはblockやinlineなど、配置の基本方式に関わります。高度なFlexboxやGridはここでは扱いません。"),
                code(".card {\n    margin: 12px;\n    padding: 16px;\n    border: 1px solid gray;\n    width: 240px;\n    display: block;\n}", "カードの外側に12px、内側に16pxの余白を作り、境界と幅を指定します。", "css"),
                warning("marginとpaddingを両方『余白』とだけ覚えると、どちらを変えるべきか迷います。境界の外側か内側かで区別してください。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("colorは文字色です。", "background-colorは背景色です。", "font-sizeは文字の大きさです。", "marginは外側、paddingは内側の余白です。", "borderは境界線です。", "widthとdisplayは配置に関わります。")),
        ],
    },
    "javascript": {
        "objective": "JavaScriptがブラウザーで操作に反応できることを説明し、HTML/CSSとの役割を区別できる。",
        "why": "ボタン操作後にページの一部を変えるような振る舞いを理解するためです。",
        "connection": "HTMLが構造、CSSが見た目でした。JavaScriptは操作に応じた動きも追加できます。",
        "sections": [
            section("動きを追加する言語",
                paragraph("JavaScriptはブラウザーでプログラムを動かすために使われる言語です。クリックなどのイベントに応じて処理できます。HTMLの構造やCSSの見た目を書き換えたり、必要ならサーバーと通信したりします。JavaScriptを使わないWebページもあります。"),
                code("<button id=\"hello\">押す</button>\n<script>\n  document.getElementById('hello').addEventListener('click', function () {\n    alert('Hello');\n  });\n</script>", "ボタンを特定し、clickイベントのときHelloを表示します。", "html"),
                table(["技術", "主な役割"], [["HTML", "内容と構造"], ["CSS", "見た目と配置"], ["JavaScript", "動きや操作への反応"]])
            ),
            section("イベントと処理の関係",
                paragraph("上の例ではgetElementByIdがidでボタンを探し、addEventListenerがclick時の処理を登録します。ページを開いた瞬間にalertが実行されるのではなく、押したときに実行されます。詳しい文法は後の学習対象ですが、どこで何が起こるかを読めれば十分です。"),
                flow("HTMLのボタンを表示", "JavaScriptがクリック時の処理を登録", "利用者がクリック", "登録した処理が動く"),
                warning("JavaScriptがないとフォームを送れない、というわけではありません。HTMLのformとsubmitでもサーバーへ送信できます。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("JavaScriptはブラウザー上で動きを追加できます。", "イベントはクリックなどの出来事です。", "処理を登録すると操作時に動きます。", "HTML/CSS/JavaScriptの役割は異なります。", "すべてのページにJavaScriptが必須ではありません。")),
        ],
    },
    "dom": {
        "objective": "DOMをHTMLの要素を扱う構造として説明し、入力取得から画面更新までの流れを追える。",
        "why": "JavaScriptがどの要素を読み、どの表示を変えるのか理解するためです。",
        "connection": "前のUNITでJavaScriptがボタンに反応しました。今回はページ内の要素と入力値を扱います。",
        "sections": [
            section("DOMはページの要素を表す",
                paragraph("DOM（Document Object Model）は、ブラウザーがHTML文書をプログラムから扱えるようにした構造です。document.getElementById('message')はidがmessageの要素を取得します。HTMLファイルそのものとDOMは同じものではなく、ブラウザーが読み取って構築した表現です。"),
                code("<p id=\"message\">待機中</p>\n<script>\n  document.getElementById('message').textContent = '開始';\n</script>", "p要素をidで探し、textContentへ代入すると表示文字が開始へ変わります。", "html"),
                table(["用語", "役割"], [["id", "ページ内で要素を見つける目印"], ["getElementById", "idで要素を取得"], ["textContent", "要素の文字内容を扱う"]])
            ),
            section("入力から画面更新まで",
                code("<input id=\"name\">\n<button id=\"show\">表示</button>\n<p id=\"message\"></p>\n<script>\n  document.getElementById('show').addEventListener('click', function () {\n    const value = document.getElementById('name').value;\n    document.getElementById('message').textContent = value;\n  });\n</script>", "クリック時にinputのvalueを読み、pのtextContentへ代入します。", "html"),
                flow("利用者がinputへ入力", "buttonを押す", "JavaScriptがvalueを読む", "DOMのtextContentを更新", "画面表示が変わる"),
                paragraph("この例ではブラウザー内の表示が変わるだけで、サーバーへ自動送信しているわけではありません。Flaskへ値を送るにはform等によるRequestが必要です。"),
                warning("利用者入力をHTMLとして無条件に挿入すると問題を生む場合があります。この例では文字内容を扱うtextContentを使います。")
            ),
            section("このUNITで必ず理解しておくこと", key_points("DOMはブラウザーが扱う文書の構造です。", "idで要素を探せます。", "inputのvalueで現在の入力を読めます。", "textContentで文字表示を変えられます。", "画面更新とサーバー送信は別です。")),
        ],
    },
}

MORE_EXAMPLES = {
    "html": section("画面に見えるものとコードの違い",
        paragraph("<p>Hello</p>をブラウザーが解釈すると、利用者には通常Helloという文字が段落として見えます。タグの文字そのものをそのまま本文に表示するわけではありません。表示がどう見えるかはブラウザーやCSSでも変わりますが、段落という意味はHTMLに残ります。"),
        paragraph("タグと属性は役割が違います。aはリンクという要素の種類、hrefはそのリンクがどこへ進むかという追加情報です。コードを読むときは『要素の意味→属性→中身』の順で確認します。")
    ),
    "document": section("headとbodyを見分ける",
        paragraph("titleをheadからbodyへ移すと、文書の題名としての役割を正しく表せません。ページ上へ見出しを置くにはbody内のh1などを使います。タブ名と画面の見出しは似た文章にできますが、別の要素です。"),
        paragraph("この骨組みの中にCSSへのlinkやJavaScriptのscriptを置く場合もあります。すべての詳細を今暗記する必要はなく、文書の設定情報と主な内容を分けることが重要です。")
    ),
    "text": section("読者が読み進める順序",
        paragraph("ページの大見出しの下に節見出しがあり、その下に説明の段落が続くと、読者は何の話かを追いやすくなります。h1の次に突然h5を使って見た目だけを合わせるより、文書の階層を先に考えます。"),
        paragraph("CSSでh2を大きく表示したり、pを太字にしたりしても、HTML上のh2は見出し、pは段落です。意味をHTMLで表し、見た目をCSSで整える分担を守ります。")
    ),
    "media": section("移動先と説明文の違い",
        paragraph("a要素の表示文字が『訓練一覧』でも、実際の移動先はhrefの値です。リンクの文字だけを見てURLを決めつけないでください。img要素でも、srcは画像の場所、altは画像が伝える内容や機能の説明であり、互いの代わりにはなりません。"),
        paragraph("画像が読めない場合にaltが役立ちます。リストの順序が重要かも同じように利用者の理解へ影響します。単なる見た目だけでタグや属性を選ばないことが大切です。")
    ),
    "forms": section("フォームとサーバー処理をつなぐ",
        paragraph("利用者が回答欄へ値を入れてsubmitすると、ブラウザーはformのmethodとactionを読み、入力名と値をまとめてRequestを作ります。サーバーはそのURLで受け取り、値を確認してResponseを返します。HTMLのformだけで正誤判定が完成するわけではありません。"),
        paragraph("GETとPOSTは送る内容の秘密性を直接決めません。URLに現れる可能性や再読み込みの振る舞いなどを考え、用途に合わせて選びます。通信保護にはHTTPSが関係します。")
    ),
    "inputs": section("nameと入力値の対応",
        paragraph("name='answer'の欄に2と入力すれば、送信時にはanswerという項目と2という値が結び付きます。サーバー側は項目名で値を探します。入力欄の上に『回答』と表示しても、それだけでは送信名は決まりません。"),
        paragraph("button type='submit'はフォームを送る役割です。button type='button'はそれ自体では通常フォームを送信しません。ボタンの見た目が同じでもtypeによって動作が違うため、コードで確認します。")
    ),
    "css": section("規則を読む順序",
        paragraph("button { padding: 12px; }なら、まずbuttonというセレクタから対象を探し、次にpaddingというプロパティを読み、最後に12pxという値を確認します。これで『ボタンの内側の余白を12pxにする』と説明できます。"),
        paragraph("同じページに多数のボタンがあれば、タグ名のセレクタはそれらへ広く適用されます。一部だけ変えたい場合はclassなどの目印を使いますが、細かな優先順位はここでは扱いません。")
    ),
    "css_layout": section("境界の内側と外側",
        paragraph("カードの文字が枠線に近すぎるならpaddingを増やします。カード同士が詰まりすぎているならmarginを調整します。同じ『狭い』でも、境界の内側か外側かで使うプロパティが違います。"),
        paragraph("widthを大きな固定値にするとスマートフォンの狭い画面からはみ出し得ます。見た目を確認するときは一つの画面幅だけで判断せず、利用する画面の大きさも考えます。")
    ),
    "javascript": section("動きと通信を分ける",
        paragraph("クリック時にalertを出す例はブラウザー内だけで完結します。一方、フォーム送信ではブラウザーからサーバーへHTTP Requestが送られます。JavaScriptから通信する方法もありますが、ここでは『ブラウザー内の処理』と『サーバーへの要求』を分けて理解します。"),
        paragraph("JavaScriptがボタンを操作できるのは、ブラウザーがHTMLをDOMとして扱えるからです。次のUNITでは、特定の要素を探して表示を変える流れを学びます。")
    ),
    "dom": section("画面だけ変えた場合を確認する",
        paragraph("inputのvalueを読み、pのtextContentへ入れれば、見える文字は変わります。しかしサーバー上のデータやSessionは、この処理だけでは変わりません。ページを再読み込みしたとき表示が元に戻る場合がある理由も、保存や送信をしていないからです。"),
        paragraph("値をサーバーへ保存したいなら、form送信など別のRequestが必要です。この違いは次のFlask訓練で、ブラウザーとPython関数をつなげるときに重要です。")
    ),
}

for lesson_id, extra in MORE_EXAMPLES.items():
    CHAPTERS[lesson_id]["sections"].insert(-1, extra)
