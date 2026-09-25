"""正式第2訓練の節末問題と章末BOSS。コードは実行せずASTで採点する。"""

from src.python_basics_1_chapters import CHAPTERS


def code_question(prompt, answer, explanation, *alternatives):
    question = {"prompt": prompt, "answer": answer, "explanation": explanation}
    if alternatives:
        question["accepted_answers"] = list(alternatives)
    return question


def choice_question(prompt, options, answer, explanation, hint):
    return {"mode": "choice", "prompt": prompt, "options": options, "answer": answer,
            "explanation": explanation, "hint": hint}


def review(prompt, source, valid, explanation, answer=None, alternatives=None):
    question = {"type": "debug", "prompt": prompt, "code": source,
                "valid": valid, "explanation": explanation}
    if answer is not None:
        question["answer"] = answer
    if alternatives:
        question["accepted_answers"] = alternatives
    return question


PYTHON_BASICS_1_COURSE = {
    "title": "Python基礎Ⅰ訓練",
    "description": "Pythonのコードを読み書きし、値・計算・条件分岐を理解する正式訓練。",
    "question_mode": "code",
    "curriculum_number": 2,
    "lesson_label": "UNIT",
    "boss_name": "PYTHON LOGIC CORE",
    "lessons": [
        {"id": "program", "title": "Pythonとプログラム", "summary": "保存されたコードをPythonが読み、OS上で実行する流れを学びます。", "questions": [
            choice_question("Pythonのソースコードを保存するファイルによく使う拡張子は？", [".jpg", ".py", ".txtだけ", ".css"], 1, ".pyはPythonコードのファイルによく使う名前の目印です。", "画像や見た目の指定とは用途が異なります。"),
            choice_question("app.pyが保存されているだけの場合、正しい説明は？", ["必ず実行中", "保存と実行は別", "CPUがソースコードをそのまま読む", "OSが不要"], 1, "ファイルがあるだけではプロセスは始まりません。起動操作が必要です。", "第1訓練のプログラムとプロセスの違いを思い出しましょう。"),
            code_question("app.pyの中でHelloを表示する最小のPythonコードを書いてください。", 'print("Hello")', "Pythonがprintの呼び出しを処理し、文字列Helloを出力します。"),
            code_question("app.pyの中でPythonを表示する1行を書いてください。", 'print("Python")', "文字列を引用符で囲んでprintへ渡します。詳しい文法は次のUNITで確認します。"),
        ]},
        {"id": "print", "title": "print", "summary": "関数の呼び出しと文字列表示を学びます。", "questions": [
            code_question("Helloを表示するコードを書いてください。", 'print("Hello")', "文字列Helloを引用符で囲み、printの引数として渡します。"),
            code_question("開始を表示するコードを書いてください。", 'print("開始")', "printへ文字列を渡すと、その内容が出力されます。"),
            code_question("1行目に開始、2行目に完了と表示するコードを書いてください。", 'print("開始")\nprint("完了")', "Pythonは上から順に二つのprintを実行します。"),
            code_question("文字列scoreを、そのまま文字として表示してください。", 'print("score")', "引用符で囲むと変数名ではなく文字列そのものになります。"),
        ]},
        {"id": "variables", "title": "変数", "summary": "値に名前を付け、代入・再代入します。", "questions": [
            code_question("変数scoreに100を代入してください。", "score = 100", "=の右側の整数100を左側の名前scoreへ結び付けます。"),
            code_question("変数nameに文字列Aliceを代入してください。", 'name = "Alice"', "引用符を付けて文字列の値を作り、nameへ代入します。"),
            code_question("scoreが定義済みです。その値を表示してください。", "print(score)", "引用符を付けずに名前を書くと、変数が参照する値を使います。"),
            code_question("scoreが定義済みです。現在の値に10を足してscoreへ再代入してください。", "score = score + 10", "右側で現在値に10を足してから、結果を同じ変数へ代入します。", "score += 10"),
        ]},
        {"id": "types", "title": "データ型", "summary": "str・int・float・boolを区別します。", "questions": [
            code_question("変数nameに文字列Aliceを代入してください。", 'name = "Alice"', "引用符を付けたAliceはstrの値です。"),
            code_question("変数countに整数10を代入してください。文字列にしないでください。", "count = 10", "引用符のない10はintです。"),
            code_question("変数rateに小数0.75を代入してください。", "rate = 0.75", "小数の0.75はfloatの値です。"),
            code_question("変数is_activeに真偽値Trueを代入してください。", "is_active = True", "Trueは先頭が大文字のbool値です。引用符で囲むと文字列になります。"),
        ]},
        {"id": "arithmetic", "title": "算術演算子", "summary": "数値の計算結果を変数へ保存します。", "questions": [
            code_question("変数totalに3 + 2の計算結果を代入してください。", "total = 3 + 2", "右側の加算が評価され、その結果をtotalへ代入します。", "total = 2 + 3"),
            code_question("priceとquantityが定義済みです。掛け算した結果をtotalへ代入してください。", "total = price * quantity", "*は乗算で、二つの現在値を掛けた結果がtotalに入ります。", "total = quantity * price"),
            code_question("変数remainingに10から3を引いた結果を代入してください。", "remaining = 10 - 3", "-は減算です。10と3の順番を逆にすると結果が変わります。"),
            code_question("変数remainderに7を3で割った余りを代入してください。", "remainder = 7 % 3", "%は余りを求める演算子で、7 % 3は1です。"),
        ]},
        {"id": "comparison", "title": "比較演算子", "summary": "値を比較してTrue/Falseを得ます。", "questions": [
            code_question("scoreが定義済みです。70以上かの結果をpassedへ代入してください。", "passed = score >= 70", ">=は70を含む比較で、結果はboolです。", "passed = 70 <= score"),
            code_question("xが定義済みです。xが10と等しいかの結果をsameへ代入してください。", "same = x == 10", "==は比較で、=の代入とは異なります。", "same = 10 == x"),
            code_question("xが定義済みです。xが0と等しくないかの結果をnonzeroへ代入してください。", "nonzero = x != 0", "!=は二つの値が異なるかを調べ、boolを返します。", "nonzero = 0 != x"),
            code_question("ageが定義済みです。18より小さいかの結果をminorへ代入してください。", "minor = age < 18", "<は18を含みません。18ちょうどならFalseです。", "minor = 18 > age"),
        ]},
        {"id": "logic", "title": "論理演算子", "summary": "複数のbool条件を組み合わせます。", "questions": [
            code_question("ageとhas_idが定義済みです。18歳以上かつIDありの結果をcan_enterへ代入してください。", "can_enter = age >= 18 and has_id", "andは年齢条件とhas_idの両方がTrueのときTrueです。", "can_enter = has_id and age >= 18"),
            code_question("is_studentとis_staffが定義済みです。どちらかを満たす結果をallowedへ代入してください。", "allowed = is_student or is_staff", "orは少なくとも一方がTrueならTrueです。両方TrueでもTrueです。", "allowed = is_staff or is_student"),
            code_question("is_closedが定義済みです。その真偽を反転してis_openへ代入してください。", "is_open = not is_closed", "notはboolのTrueとFalseを反転します。"),
            code_question("scoreとattendedが定義済みです。70点以上かつ出席済みの結果をpassedへ代入してください。", "passed = score >= 70 and attended", "比較の結果と出席のboolが両方TrueのときだけpassedはTrueです。", "passed = attended and score >= 70"),
        ]},
        {"id": "if", "title": "if", "summary": "条件がTrueのときだけ処理します。", "questions": [
            code_question("scoreが定義済みです。70点以上なら合格を表示する完成したif文を書いてください。", 'if score >= 70:\n    print("合格")', "コロンの後に字下げしたprintを置き、条件がTrueのときだけ表示します。", 'if 70 <= score:\n    print("合格")'),
            code_question("ageが定義済みです。18歳未満なら未成年を表示してください。", 'if age < 18:\n    print("未成年")', "18は含まず、条件がTrueのときだけ字下げ部分を実行します。", 'if 18 > age:\n    print("未成年")'),
            code_question("is_activeが定義済みです。Trueなら稼働中を表示するif文を書いてください。", 'if is_active:\n    print("稼働中")', "boolの変数を条件式に使えます。Trueのときだけ表示します。", 'if is_active == True:\n    print("稼働中")'),
            code_question("scoreとattendedが定義済みです。70点以上かつ出席済みなら合格を表示してください。", 'if score >= 70 and attended:\n    print("合格")', "比較とandを組み合わせた条件全体がTrueならブロックを実行します。", 'if attended and score >= 70:\n    print("合格")'),
        ]},
        {"id": "elif", "title": "elif", "summary": "複数の条件を上から順に調べます。", "questions": [
            code_question("scoreが定義済みです。80点以上ならA、そうでなく60点以上ならBを表示してください。", 'if score >= 80:\n    print("A")\nelif score >= 60:\n    print("B")', "高い基準から調べ、最初にTrueになった枝だけを実行します。"),
            code_question("temperatureが定義済みです。30以上なら暑い、そうでなく20以上なら暖かいと表示してください。", 'if temperature >= 30:\n    print("暑い")\nelif temperature >= 20:\n    print("暖かい")', "30以上を先に置かないと、その範囲が後の20以上に含まれます。"),
            code_question("levelが定義済みです。5以上なら上級、そうでなく3以上なら中級を表示してください。", 'if level >= 5:\n    print("上級")\nelif level >= 3:\n    print("中級")', "elifは前の条件がFalseのときだけ評価されます。"),
            code_question("scoreが定義済みです。100なら満点、そうでなく70以上なら合格と表示してください。", 'if score == 100:\n    print("満点")\nelif score >= 70:\n    print("合格")', "等しさの比較は==です。最初に満点を調べます。"),
        ]},
        {"id": "else", "title": "else", "summary": "どの条件にも当てはまらない場合を扱います。", "questions": [
            code_question("scoreが定義済みです。80以上ならA、そうでなく60以上ならB、それ以外はCを表示してください。", 'if score >= 80:\n    print("A")\nelif score >= 60:\n    print("B")\nelse:\n    print("C")', "上から判定し、どの条件も成立しない場合だけelseを実行します。"),
            code_question("ageが定義済みです。18以上なら成人、それ以外は未成年と表示してください。", 'if age >= 18:\n    print("成人")\nelse:\n    print("未成年")', "elseはifがFalseだった残りの場合を受け持ちます。"),
            code_question("scoreとattendedが定義済みです。70以上かつ出席済みなら合格、それ以外は再確認と表示してください。", 'if score >= 70 and attended:\n    print("合格")\nelse:\n    print("再確認")', "条件全体がFalseならelseへ進みます。"),
            code_question("temperatureが定義済みです。30以上なら暑い、20以上なら暖かい、それ以外は寒いと表示してください。", 'if temperature >= 30:\n    print("暑い")\nelif temperature >= 20:\n    print("暖かい")\nelse:\n    print("寒い")', "高い境界から順に調べ、残りをelseで扱います。"),
        ]},
    ],
    "boss": [
        review("要件：Helloを表示する。このコードは正しいか？", 'print("Hello")', True, "printへ文字列を渡しているため、Helloを表示します。"),
        review("要件：Helloという文字を表示する。このコードは正しいか？", "print(Hello)", False, "引用符がないHelloは変数名として読まれます。文字列を表示するには引用符が必要です。", 'print("Hello")'),
        review("要件：整数100をscoreへ入れて表示する。このコードは正しいか？", "score = 100\nprint(score)", True, "整数を代入し、変数の値を表示しています。"),
        review("要件：countへ整数10を代入する。このコードは正しいか？", 'count = "10"', False, "引用符付きの10はstrです。整数にするには引用符を外します。", "count = 10"),
        review("要件：priceとquantityの積をtotalへ入れる。このコードは正しいか？", "total = price + quantity", False, "加算では数量分の合計額になりません。積には*を使います。", "total = price * quantity", ["total = quantity * price"]),
        review("要件：xが10と等しいかをsameへ入れる。このコードは正しいか？", "same = x = 10", False, "連続代入では比較結果を得られません。等しさは==で調べます。", "same = x == 10", ["same = 10 == x"]),
        review("要件：80点以上なら合格を表示する。このコードは正しいか？", 'if score > 80:\n    print("合格")', False, "構文は動きますが80点ちょうどを除外しています。境界を含む>=が必要です。", 'if score >= 80:\n    print("合格")', ['if 80 <= score:\n    print("合格")']),
        review("要件：18歳以上かつIDありなら入場と表示する。このコードは正しいか？", 'if age >= 18 or has_id:\n    print("入場")', False, "orでは一方だけ満たしても入れます。両方必要なのでandを使います。", 'if age >= 18 and has_id:\n    print("入場")', ['if has_id and age >= 18:\n    print("入場")']),
        review("要件：70点以上なら合格を表示する。このコードは正しいか？", 'if score >= 70\n    print("合格")', False, "if行の末尾にコロンが必要です。字下げした処理も保ちます。", 'if score >= 70:\n    print("合格")'),
        review("要件：80以上はA、60以上はBを表示する。このコードは正しいか？", 'if score >= 60:\n    print("B")\nelif score >= 80:\n    print("A")', False, "80以上は先の60以上に当てはまり、Aへ到達しません。高い基準を先に調べます。", 'if score >= 80:\n    print("A")\nelif score >= 60:\n    print("B")'),
        review("要件：18以上は成人、それ以外は未成年と表示する。このコードは正しいか？", 'if age >= 18:\n    print("成人")\nelse:\nprint("未成年")', False, "elseの中のprintもインデントが必要です。", 'if age >= 18:\n    print("成人")\nelse:\n    print("未成年")'),
        review("要件：70点以上かつ出席済みなら合格、それ以外は再確認と表示する。このコードは正しいか？", 'if score >= 70 and attended:\n    print("合格")\nelse:\n    print("再確認")', True, "比較・and・if/elseがつながり、両方の条件を満たすときだけ合格を表示します。"),
    ],
}

for lesson in PYTHON_BASICS_1_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])
