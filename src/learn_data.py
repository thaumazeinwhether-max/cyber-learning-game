"""Learnフェーズの教材と問題。画面表示と進行処理から分けて管理する。"""

from src.computer_os_data import COMPUTER_OS_COURSE


COURSES = {
    "computer_os": COMPUTER_OS_COURSE,
    "it": {
        "title": "IT基礎訓練",
        "description": "コンピュータ、ネットワーク、Webの基本を学ぶコース。",
        "question_mode": "choice",
        "lessons": [
            {
                "id": "computer",
                "title": "コンピュータの基本",
                "summary": "コンピュータは、計算・一時保存・長期保存を分担しています。",
                "points": [
                    {"term": "CPU", "text": "命令に従って計算や処理をする部分。", "example": "人にたとえると、考えて作業する役です。"},
                    {"term": "RAM", "text": "作業中のデータを一時的に置く場所。電源を切ると内容は消えます。", "example": "机の上に広げたノートのような場所です。"},
                    {"term": "ストレージ", "text": "ファイルを長く保存する場所。", "example": "写真や文書を保存するときに使います。"},
                ],
                "takeaway": "CPUは処理、RAMは一時保存、ストレージは長期保存。",
                "questions": [
                    {"prompt": "計算や処理を担当するのはどれ？", "options": ["CPU", "RAM", "ストレージ", "画面"], "answer": 0, "explanation": "CPUが命令に従って処理します。"},
                    {"prompt": "電源を切ると内容が消える一時的な作業場所は？", "options": ["ストレージ", "RAM", "画面", "キーボード"], "answer": 1, "explanation": "RAMは作業中のデータを一時的に置きます。"},
                ],
            },
            {
                "id": "network",
                "title": "ネットワークの基本",
                "summary": "ネットワークでは、依頼する側と応答する側が情報をやり取りします。",
                "points": [
                    {"term": "クライアント / サーバー", "text": "クライアントが依頼し、サーバーが応答します。", "example": "ブラウザーがページを要求し、サーバーが返します。"},
                    {"term": "IPアドレス", "text": "ネットワーク上の機器を見つけるための番号です。", "example": "通信の届け先を示す住所のようなものです。"},
                    {"term": "DNS", "text": "ドメイン名とIPアドレスを対応付ける仕組みです。", "example": "名前から通信先の番号を調べます。"},
                ],
                "takeaway": "クライアントが依頼し、IPアドレスで届け先を見つけ、サーバーが応答します。",
                "questions": [
                    {"prompt": "Webページを要求するブラウザーはどちら？", "options": ["サーバー", "クライアント", "DNS", "ストレージ"], "answer": 1, "explanation": "依頼する側がクライアントです。"},
                    {"prompt": "ネットワーク上の機器を見つける番号は？", "options": ["RAM", "HTTP", "IPアドレス", "CPU"], "answer": 2, "explanation": "IPアドレスは通信先を見つけるための番号です。"},
                ],
            },
            {
                "id": "web",
                "title": "Webの基本",
                "summary": "Webページは、ブラウザーとWebサーバーのやり取りで表示されます。",
                "points": [
                    {"term": "ブラウザー", "text": "Webページを見たり、サーバーへページを要求したりするアプリです。", "example": "アドレスを入力してページを開きます。"},
                    {"term": "Webサーバー", "text": "要求されたWebページのデータを返します。", "example": "ブラウザーからの要求を受け取ります。"},
                    {"term": "HTTP", "text": "ブラウザーとWebサーバーが情報をやり取りするときの約束です。", "example": "ページを要求し、結果を受け取るときに使います。"},
                ],
                "takeaway": "ブラウザーがHTTPで要求し、Webサーバーがページを返します。",
                "questions": [
                    {"prompt": "Webページのデータを返すのは？", "options": ["Webサーバー", "RAM", "CPU", "キーボード"], "answer": 0, "explanation": "Webサーバーが要求されたページのデータを返します。"},
                    {"prompt": "ブラウザーとWebサーバーのやり取りの約束は？", "options": ["DNS", "HTTP", "RAM", "ストレージ"], "answer": 1, "explanation": "HTTPはWebで情報をやり取りするための約束です。"},
                ],
            },
        ],
        "boss": [
            {"type": "true_false", "prompt": "RAMは電源を切っても内容を保持する。", "answer": "false", "explanation": "RAMの内容は電源を切ると消えます。"},
            {"type": "term", "prompt": "ドメイン名とIPアドレスを対応付ける仕組みは？", "answer": "DNS", "explanation": "DNSが名前とIPアドレスを対応付けます。"},
            {"type": "true_false", "prompt": "ブラウザーはHTTPを使ってWebサーバーにページを要求できる。", "answer": "true", "explanation": "ブラウザーとWebサーバーはHTTPでやり取りします。"},
        ],
    },
    "python": {
        "title": "Python基礎訓練",
        "description": "変数、条件分岐、繰り返しをコードで学ぶコース。",
        "question_mode": "code",
        "lessons": [
            {
                "id": "variables",
                "title": "変数と print",
                "summary": "変数に値を入れ、printで画面に表示します。",
                "points": [
                    {"term": "代入", "text": "= の右側の値を、左側の変数へ入れます。", "example": "x = 10 なら x に10が入ります。"},
                    {"term": "print", "text": "括弧の中の値を表示します。", "example": "print('Hello') は Hello を表示します。"},
                ],
                "code": "x = 10\nprint(x)",
                "code_explanation": "最初の行で x に10を入れ、次の行で x の値を表示します。",
                "takeaway": "= は代入、print(...) は表示。",
                "questions": [
                    {"prompt": "変数 x に10を代入してください。", "answer": "x = 10", "explanation": "= の左に変数名、右に入れる値を書きます。"},
                    {"prompt": "Hello という文字を表示してください。", "answer": "print('Hello')", "explanation": "文字は引用符で囲み、print の括弧に入れます。"},
                ],
            },
            {
                "id": "conditions",
                "title": "条件分岐",
                "summary": "if を使うと、条件に応じて処理を変えられます。",
                "points": [
                    {"term": "if", "text": "条件が成り立つ場合に、字下げした行を実行します。", "example": "年齢が18以上のときだけ表示できます。"},
                    {"term": ": と字下げ", "text": "条件の末尾に : を書き、次の行を字下げします。", "example": "if age >= 18: の次に4つの空白を入れます。"},
                ],
                "code": "age = 20\nif age >= 18:\n    print('adult')",
                "code_explanation": "age が18以上なので、adult が表示されます。",
                "takeaway": "if 条件: の次の行を字下げする。",
                "questions": [
                    {"prompt": "age が18以上なら adult と表示する if 文を書いてください。age はすでに定義されています。", "answer": "if age >= 18:\n    print('adult')", "explanation": "if の末尾に : を書き、print を字下げします。"},
                    {"prompt": "score が60以上なら pass と表示する if 文を書いてください。score はすでに定義されています。", "answer": "if score >= 60:\n    print('pass')", "explanation": "比較には >= を使い、次の行を字下げします。"},
                ],
            },
            {
                "id": "loops",
                "title": "繰り返し",
                "summary": "for を使うと、同じ処理を何度も行えます。",
                "points": [
                    {"term": "for", "text": "指定した回数だけ、字下げした行を繰り返します。", "example": "for i in range(3): なら3回です。"},
                    {"term": "range", "text": "range(3) は 0、1、2 を順番に作ります。", "example": "print(i) で 0、1、2 が表示されます。"},
                ],
                "code": "for i in range(3):\n    print(i)",
                "code_explanation": "i が0、1、2と変わり、そのたびに値を表示します。",
                "takeaway": "for 変数 in range(回数): の次の行を字下げする。",
                "questions": [
                    {"prompt": "i を使って3回繰り返し、そのたびに i を表示してください。", "answer": "for i in range(3):\n    print(i)", "explanation": "range(3) で3回繰り返し、print(i) を字下げします。"},
                    {"prompt": "n を使って2回繰り返し、そのたびに n を表示してください。", "answer": "for n in range(2):\n    print(n)", "explanation": "range(2) は 0 と 1 を作ります。"},
                ],
            },
        ],
        "boss": [
            {"type": "debug", "prompt": "このコードは正しいか？", "code": "age = 20\nif age >= 18\n    print('adult')", "valid": False, "answer": "age = 20\nif age >= 18:\n    print('adult')", "explanation": "if の条件の末尾に : が必要です。"},
            {"type": "debug", "prompt": "このコードは正しいか？", "code": "for i in range(2):\n    print(i)", "valid": True, "explanation": "for の末尾に : があり、次の行も字下げされています。"},
            {"type": "debug", "prompt": "このコードは正しいか？", "code": "print 'Hello'", "valid": False, "answer": "print('Hello')", "explanation": "Python 3では print の内容を括弧で囲みます。"},
        ],
    },
}


def get_lesson(course, lesson_id):
    for lesson in course["lessons"]:
        if lesson["id"] == lesson_id:
            return lesson
    return None
