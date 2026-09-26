"""正式第5訓練の節末問題とコードレビューBOSS。回答コードは実行しない。"""

from src.python_basics_2_chapters import CHAPTERS


def code_question(prompt, answer, explanation, *alternatives):
    item = {"prompt": prompt, "answer": answer, "explanation": explanation}
    if alternatives:
        item["accepted_answers"] = list(alternatives)
    return item


def review(prompt, source, valid, explanation, answer=None, alternatives=()):
    item = {"type": "debug", "prompt": prompt, "code": source,
            "valid": valid, "explanation": explanation}
    if answer is not None:
        item["answer"] = answer
    if alternatives:
        item["accepted_answers"] = list(alternatives)
    return item


PYTHON_BASICS_2_COURSE = {
    "title": "Python基礎Ⅱ訓練",
    "description": "繰り返し、データのまとまり、関数、例外、デバッグをコードで学ぶ正式訓練。",
    "question_mode": "code",
    "curriculum_number": 5,
    "lesson_label": "UNIT",
    "boss_name": "PYTHON PROGRAM CORE",
    "lessons": [
        {"id": "for_range", "title": "forとrange", "summary": "0始まりの数を使い、処理を決めた回数だけ繰り返します。", "questions": [
            code_question("変数名をiとして、0、1、2を順に表示する完成したfor文を書いてください。", "for i in range(3):\n    print(i)", "range(3)は0から2までの3個の値を渡します。"),
            code_question("変数名をiとして、1、2、3を順に表示するfor文を書いてください。", "for i in range(1, 4):\n    print(i)", "開始1、終了4は含まれないため1〜3を表示します。"),
            code_question("「確認」を2回表示するfor文を書いてください。変数名はiとします。", "for i in range(2):\n    print('確認')", "range(2)の値は0と1で、本体が2回動きます。"),
            code_question("変数名をiとして0、1を表示し、ループ終了後に「終わり」を1回表示してください。", "for i in range(2):\n    print(i)\nprint('終わり')", "字下げの外のprintはループ後に1回実行されます。"),
        ]},
        {"id": "while", "title": "while", "summary": "条件を確認し、更新して終了するループを作ります。", "questions": [
            code_question("countを0に初期化し、0、1、2を表示して終わるwhile文を書いてください。", "count = 0\nwhile count < 3:\n    print(count)\n    count = count + 1", "各回でcountを増やし、3になったら条件がFalseになります。", "count = 0\nwhile count < 3:\n    print(count)\n    count += 1"),
            code_question("countを0に初期化し、countが2より小さい間、countを1増やすwhile文を書いてください。", "count = 0\nwhile count < 2:\n    count += 1", "更新を入れるとcountが2になった時点で終了します。", "count = 0\nwhile count < 2:\n    count = count + 1"),
            code_question("nを3に初期化し、3、2、1を表示して終わるwhile文を書いてください。", "n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1", "各回でnを1減らすので、0になったら終了します。", "n = 3\nwhile n > 0:\n    print(n)\n    n -= 1"),
            code_question("countを3に初期化し、条件count < 3がFalseなので本体を実行しないwhile文を書いてください。本体はprint(count)とします。", "count = 3\nwhile count < 3:\n    print(count)", "whileは本体の前に条件を確認し、最初からFalseなら動きません。"),
        ]},
        {"id": "list", "title": "list", "summary": "順序のある複数の値を取得・追加します。", "questions": [
            code_question("変数scoresへ70、80、90のlistを代入してください。", "scores = [70, 80, 90]", "角括弧で順番のある三つの要素を作ります。"),
            code_question("scoresが定義済みです。最初の要素を表示してください。", "print(scores[0])", "listのインデックスは0から始まります。"),
            code_question("scoresが定義済みです。末尾に100を追加してください。", "scores.append(100)", "appendは元のlistの末尾へ要素を追加します。", "scores += [100]"),
            code_question("scoresが定義済みです。三つ目の要素をthird_scoreへ代入してください。", "third_score = scores[2]", "三つ目のインデックスは2です。"),
        ]},
        {"id": "dict", "title": "dict", "summary": "キーと値の対応で情報を扱います。", "questions": [
            code_question("nameがAlice、scoreが100のdictをuserへ代入してください。", "user = {'name': 'Alice', 'score': 100}", "キーと値をコロンで対応付けます。", "user = {'score': 100, 'name': 'Alice'}"),
            code_question("userが定義済みです。nameキーの値を表示してください。", "print(user['name'])", "dictはキーで値を取得します。"),
            code_question("userが定義済みです。scoreキーの値を110へ更新してください。", "user['score'] = 110", "キーで対応する値へ代入すると更新できます。"),
            code_question("変数settingsへ、キーmodeの値がstudyであるdictを代入してください。", "settings = {'mode': 'study'}", "波括弧の中にキー: 値を一組書きます。"),
        ]},
        {"id": "functions", "title": "関数", "summary": "defで処理をまとめ、必要な時に呼び出します。", "questions": [
            code_question("呼ぶとHelloを表示するgreet関数を定義してください。", "def greet():\n    print('Hello')", "defで定義し、字下げした本体に表示処理を書きます。"),
            code_question("greet関数が定義済みです。1回呼び出してください。", "greet()", "括弧を付けた呼び出しで本体が実行されます。"),
            code_question("呼ぶと「開始」を表示するstart関数を定義し、その後1回呼んでください。", "def start():\n    print('開始')\n\nstart()", "定義だけでは表示されず、最後の呼び出しで動きます。"),
            code_question("呼ぶと1、2の順に表示するshow関数を定義してください。", "def show():\n    print(1)\n    print(2)", "二つの字下げ行が関数本体です。"),
        ]},
        {"id": "arguments", "title": "引数とreturn", "summary": "値を渡し、結果を呼び出し元へ返します。", "questions": [
            code_question("aとbを受け取り、その和を返すadd関数を定義してください。", "def add(a, b):\n    return a + b", "returnは結果を呼び出し元へ返します。", "def add(a, b):\n    return b + a"),
            code_question("add関数が定義済みです。10と20を渡した返り値をresultへ代入してください。", "result = add(10, 20)", "二つの実引数を渡し、返り値を変数へ保存します。"),
            code_question("nameを受け取り、その値をそのまま返すidentity関数を定義してください。", "def identity(name):\n    return name", "printではなくreturnを使うと呼び出し元が値を使えます。"),
            code_question("numberを受け取り2倍の値を返すdouble関数を定義してください。", "def double(number):\n    return number * 2", "引数の値から計算し、結果を返します。", "def double(number):\n    return 2 * number", "def double(number):\n    return number + number"),
        ]},
        {"id": "scope", "title": "変数スコープの基礎", "summary": "関数内の名前と外の名前を区別します。", "questions": [
            code_question("引数numberを2倍にした値を返すdoubled関数を、ローカル変数resultを使って定義してください。", "def doubled(number):\n    result = number * 2\n    return result", "resultは関数内のローカル変数で、returnにより値を外へ渡します。", "def doubled(number):\n    result = 2 * number\n    return result", "def doubled(number):\n    result = number + number\n    return result"),
            code_question("関数内のローカル変数scoreへ20を入れ、表示するshow_score関数を定義してください。", "def show_score():\n    score = 20\n    print(score)", "関数内で代入したscoreはこの関数のローカルです。"),
            code_question("引数valueをローカル変数copyへ代入して返すcopy_value関数を定義してください。", "def copy_value(value):\n    copy = value\n    return copy", "関数内のcopyをreturnで呼び出し元へ渡します。"),
            code_question("doubled関数が定義済みです。3を渡して返り値をanswerへ代入してください。", "answer = doubled(3)", "内側の変数ではなく返り値を外のanswerで受け取ります。"),
        ]},
        {"id": "modules", "title": "moduleとimport", "summary": "ファイル単位の機能を読み込み再利用します。", "questions": [
            code_question("標準ライブラリのrandomモジュールを読み込んでください。", "import random", "import文でrandom内の機能を参照できるようにします。"),
            code_question("randomを読み込み、1〜3の整数を得てnumberへ代入してください。", "import random\nnumber = random.randint(1, 3)", "モジュール名付きでrandintを呼びます。"),
            code_question("標準ライブラリのmathモジュールを読み込んでください。", "import math", "mathはPythonに付属するモジュールの一つです。"),
            code_question("randomが読み込み済みです。1〜6の整数をrollへ代入してください。", "roll = random.randint(1, 6)", "random内の関数をモジュール名付きで呼び出します。"),
        ]},
        {"id": "exceptions", "title": "例外とtry / except", "summary": "想定した失敗だけを扱い、問題を隠さないようにします。", "questions": [
            code_question("int('abc')の結果をnumberへ代入しようと試し、ValueErrorのとき「数字ではありません」と表示してください。", "try:\n    number = int('abc')\nexcept ValueError:\n    print('数字ではありません')", "変換失敗だけをValueErrorとして扱います。", "try:\n    int('abc')\nexcept ValueError:\n    print('数字ではありません')"),
            code_question("textが定義済みです。int(text)の結果をnumberへ代入しようと試し、ValueErrorなら「変換失敗」と表示してください。", "try:\n    number = int(text)\nexcept ValueError:\n    print('変換失敗')", "変換処理をtryへ、指定した例外の対応をexceptへ書きます。"),
            code_question("valueが定義済みです。int(value)の結果をresultへ代入しようと試し、ValueErrorなら「確認」と表示してください。", "try:\n    result = int(value)\nexcept ValueError:\n    print('確認')", "想定した値の変換失敗だけを捕まえます。"),
            code_question("int('abc')の結果をresultへ代入しようと試し、ValueErrorなら「入力を確認」と表示してください。", "try:\n    result = int('abc')\nexcept ValueError:\n    print('入力を確認')", "例外を黙って無視せず、説明を表示します。", "try:\n    int('abc')\nexcept ValueError:\n    print('入力を確認')"),
        ]},
        {"id": "debugging", "title": "エラーの読み方とデバッグ", "summary": "エラー名と行を見て、原因を小さく確認します。", "questions": [
            code_question("未定義のnameを表示してNameErrorになる例を、nameへAliceを代入してから表示する形へ修正してください。", "name = 'Alice'\nprint(name)", "名前を参照する前に値を代入します。"),
            code_question("文字列'10'と整数5をそのまま足すTypeErrorを避け、整数へ変換した結果をtotalへ代入してください。", "total = int('10') + 5", "intで数字の文字列を整数にしてから加算します。", "total = 5 + int('10')"),
            code_question("int('abc')のValueErrorを調べるため、変数valueへ'abc'を代入し、変換前の値を表示してください。", "value = 'abc'\nprint(value)", "変換前の値を小さく確認するのが原因の切り分けです。"),
            code_question("if score >= 70 のコロン忘れを直し、合格を表示する完成したif文を書いてください。scoreは定義済みです。", "if score >= 70:\n    print('合格')", "SyntaxErrorになるコロン忘れを直し、本体を字下げします。"),
        ]},
    ],
    "boss": [
        review("要件：0、1、2を表示する。正しいか？", "for i in range(3):\n    print(i)", True, "range(3)は0〜2を順に渡します。"),
        review("要件：1、2、3を表示する。正しいか？", "for i in range(3):\n    print(i)", False, "range(3)は0〜2です。開始1、終了4に直します。", "for i in range(1, 4):\n    print(i)"),
        review("要件：0、1、2を表示して終了する。正しいか？", "count = 0\nwhile count < 3:\n    print(count)", False, "countが更新されず、条件がTrueのままです。", "count = 0\nwhile count < 3:\n    print(count)\n    count += 1", ["count = 0\nwhile count < 3:\n    print(count)\n    count = count + 1"]),
        review("要件：listの最初の得点を表示する。正しいか？", "scores = [70, 80, 90]\nprint(scores[1])", False, "インデックス1は二つ目の80です。最初は0です。", "scores = [70, 80, 90]\nprint(scores[0])"),
        review("要件：list末尾へ100を追加する。正しいか？", "scores = [70, 80]\nscores.append(100)", True, "appendは元のlistの末尾へ100を追加します。"),
        review("要件：dictのnameの値を表示する。正しいか？", "user = {'name': 'Alice'}\nprint(user[0])", False, "dictはキーで取得します。0というキーはありません。", "user = {'name': 'Alice'}\nprint(user['name'])"),
        review("要件：greetを定義しHelloを1回表示する。正しいか？", "def greet():\n    print('Hello')\ngreet()", True, "定義の後の呼び出しで本体が1回動きます。"),
        review("要件：二数の和を呼び出し元へ返す。正しいか？", "def add(a, b):\n    print(a + b)", False, "printは表示であり返り値ではありません。returnが必要です。", "def add(a, b):\n    return a + b", ["def add(a, b):\n    return b + a"]),
        review("要件：関数内の二倍値を外へ返す。正しいか？", "def doubled(n):\n    result = n * 2\n    return result", True, "ローカルの計算結果をreturnで渡します。"),
        review("次のコードを単体で実行します。事前のimportはありません。要件：random.randint(1, 3)を使いnumberへ代入する。正しいか？", "number = random.randint(1, 3)", False, "このコード単体ではrandomをimportしていません。", "import random\nnumber = random.randint(1, 3)"),
        review("要件：数字でない文字列の変換失敗を扱う。正しいか？", "try:\n    number = int('abc')\nexcept ValueError:\n    print('数字ではありません')", True, "ValueErrorを指定して入力の問題を説明します。"),
        review("要件：値の変換失敗を利用者へ説明する。正しいか？", "try:\n    number = int('abc')\nexcept ValueError:\n    pass", False, "passでは失敗を黙って隠します。説明を表示します。", "try:\n    number = int('abc')\nexcept ValueError:\n    print('数字ではありません')"),
        review("前提：scoreは定義済み。要件：70以上なら合格を表示する。正しいか？", "if score > 70:\n    print('合格')", False, "構文は動きますが、70点ちょうどが除外されます。", "if score >= 70:\n    print('合格')"),
        review("要件：数字の文字列'10'と整数5を足し15を得る。正しいか？", "total = '10' + 5", False, "型が異なる値はそのまま足せずTypeErrorです。", "total = int('10') + 5", ["total = 5 + int('10')"]),
    ],
}

for lesson in PYTHON_BASICS_2_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])
