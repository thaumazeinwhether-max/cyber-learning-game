"""正式カリキュラム第1訓練の教材・問題データ。"""

from src.computer_os_chapters import CHAPTERS

COMPUTER_OS_COURSE = {
    "title": "コンピュータ・OS基礎訓練",
    "description": "コンピュータの内部から、OS・ファイル・操作方法までをつなげて理解する。",
    "question_mode": "choice",
    "curriculum_number": 1,
    "lesson_label": "UNIT",
    "boss_name": "SYSTEM CORE",
    "lessons": [
        {
            "id": "hardware",
            "title": "コンピュータの基本構成",
            "summary": "入力された情報を処理し、一時的または長期的に保存して、結果を出力します。",
            "questions": [
                {"prompt": "プログラムの命令に従って計算や判断を進める部品は？", "options": ["CPU", "RAM", "SSD", "ディスプレイ"], "answer": 0, "hint": "処理を担当する部品を探しましょう。一時保持や長期保存とは別の役割です。", "explanation": "CPUが命令を実行し、計算や値の比較を進めます。", "wrong_explanations": {"1": "RAMは処理中の命令やデータを一時的に保持します。", "2": "SSDはファイルなどを長期保存します。", "3": "ディスプレイは処理結果を人へ出力します。"}},
                {"prompt": "作業中のデータを一時的に保持し、一般に電源を切ると内容が失われるのは？", "options": ["HDD", "RAM", "SSD", "キーボード"], "answer": 1, "hint": "机の上の作業場所に近い役割です。", "explanation": "一般的なRAMは揮発性のメモリです。"},
                {"prompt": "保存した写真を電源を切った後も残しておく主な場所は？", "options": ["CPU", "RAM", "ストレージ", "マウス"], "answer": 2, "hint": "処理中だけ使う場所ではなく、長期保存を担当する場所です。", "explanation": "SSDやHDDなどのストレージに保存します。"},
                {"prompt": "SSDとHDDの共通点として正しいものは？", "options": ["どちらも入力装置", "どちらも出力装置", "どちらもCPUの種類", "どちらもストレージの種類"], "answer": 3, "hint": "ファイルを長く残す役割を思い出しましょう。", "explanation": "SSDとHDDはどちらも長期保存に使うストレージです。"},
                {"prompt": "キーボードとディスプレイの組み合わせで正しいものは？", "options": ["両方とも入力装置", "キーボードは入力、ディスプレイは出力", "キーボードは出力、ディスプレイは入力", "両方ともストレージ"], "answer": 1, "hint": "人から情報を渡す側と、結果を人に見せる側を分けましょう。", "explanation": "キーボードで入力し、ディスプレイで結果を出力します。"},
                {"prompt": "SSDに保存したPythonファイルを起動するとき、各部品の役割として正しいものは？", "options": ["SSDが命令を処理し、CPUが長期保存する", "RAMが長期保存し、SSDが計算する", "SSDが保存し、RAMが処理中の情報を保持し、CPUが命令を処理する", "ディスプレイがコードを保存し、キーボードが計算する"], "answer": 2, "hint": "保存・一時保持・命令処理の三つを順に分けましょう。", "explanation": "ストレージが保存、RAMが一時保持、CPUが命令処理を担当します。"},
            ],
        },
        {
            "id": "os",
            "title": "OSとは",
            "summary": "OSはコンピュータの基本ソフトで、アプリや部品を使えるようにします。",
            "questions": [
                {"prompt": "次のうちOSはどれ？", "options": ["Chrome", "VS Code", "Windows", "写真ファイル"], "answer": 2, "hint": "コンピュータ全体を管理する基本ソフトを選びましょう。", "explanation": "WindowsはOSです。ChromeとVS Codeはアプリです。"},
                {"prompt": "ChromeとVS Codeの共通点は？", "options": ["どちらもOS", "どちらもアプリケーション", "どちらもCPU", "どちらもストレージ"], "answer": 1, "hint": "特定の作業を行うソフトか、全体を管理する基本ソフトかを考えましょう。", "explanation": "ChromeとVS Codeは用途の異なるアプリケーションです。"},
                {"prompt": "Linuxについて正しい説明は？", "options": ["画像形式", "プログラミング言語", "入力装置", "OS"], "answer": 3, "hint": "WindowsやmacOSと同じ分類に入ります。", "explanation": "LinuxはOSの一種であり、プログラミング言語ではありません。"},
                {"prompt": "OSが管理するものとして適切なのは？", "options": ["CPU・メモリ・ファイルなど", "ディスプレイの外枠だけ", "利用者の学習時間だけ", "Webサイトの文章だけ"], "answer": 0, "hint": "アプリが使うコンピュータの資源を思い出しましょう。", "explanation": "OSはCPU、メモリ、ストレージ、ファイル、実行中のプログラムなどを管理します。"},
                {"prompt": "アプリとOSの関係で正しいものは？", "options": ["アプリがOSを作る", "OSはアプリの種類", "アプリはOSの機能を利用して動く", "両者は常に同じもの"], "answer": 2, "hint": "基本ソフトが資源を管理し、特定の作業をするソフトがそれを利用します。", "explanation": "アプリケーションはOSの機能を利用して動きます。"},
                {"prompt": "Chrome、VS Code、Pythonアプリを同時に開いたときの説明として適切なのは？", "options": ["それぞれがCPUを永久に独占する", "OSが実行やメモリ利用を管理する", "OSは起動後に不要になる", "三つはすべて別のOSになる"], "answer": 1, "hint": "複数のアプリが同じ部品を使うとき、共通の管理役を考えましょう。", "explanation": "OSが複数アプリの実行と資源利用を管理します。"},
            ],
        },
        {
            "id": "files",
            "title": "ファイル・フォルダ・拡張子",
            "summary": "データはファイルに保存し、フォルダで整理します。名前の末尾は形式を知る手掛かりです。",
            "questions": [
                {"prompt": "このプロジェクトのsrcやtestsに当たるものは？", "options": ["CPU", "フォルダ", "拡張子", "プロセス"], "answer": 1, "hint": "ファイルをまとめて整理する入れ物です。", "explanation": "srcやtestsはファイルをまとめるフォルダです。"},
                {"prompt": "ファイル名の末尾に付く .py のような部分は？", "options": ["ディレクトリ", "OS", "拡張子", "プロセス"], "answer": 2, "hint": "名前から形式を推測するための目印です。", "explanation": ".pyは拡張子で、Pythonコードに使われます。"},
                {"prompt": "photo.jpg を photo.txt に改名しただけなら何が起きる？", "options": ["画像データが文章に変換される", "中身は変わらず名前が変わる", "必ずファイルが消える", "OSが画像を作り直す"], "answer": 1, "hint": "名前の変更とデータ形式の変換は別の操作です。", "explanation": "拡張子の変更だけでは内部データは変換されません。"},
                {"prompt": "Webページの文書に一般的に使う拡張子は？", "options": [".jpg", ".py", ".html", ".txt"], "answer": 2, "hint": "教材で挙げたWeb文書の例を思い出しましょう。", "explanation": ".htmlはWebページの文書に使います。"},
                {"prompt": "ファイル形式を最もよく説明しているものは？", "options": ["ファイルの大きさだけ", "フォルダの個数", "ファイル内のデータの作られ方", "電源の種類"], "answer": 2, "hint": "名前の末尾ではなく、中身のデータに注目します。", "explanation": "ファイル形式は中身のデータの作られ方を表します。"},
                {"prompt": "src、tests、docsを別々のフォルダにする理由として最も適切なのは？", "options": ["CPUの計算を必ず速くするため", "役割ごとにファイルを整理し、探しやすくするため", "拡張子をなくすため", "すべてのファイルを同じ形式にするため"], "answer": 1, "hint": "コード、テスト、文書を分けたときに人が得る利点を考えましょう。", "explanation": "フォルダ分けは役割ごとの整理と探索に役立ちます。"},
            ],
        },
        {
            "id": "paths",
            "title": "パス",
            "summary": "パスは、フォルダの階層の中でファイルやフォルダの場所を示します。",
            "questions": [
                {"prompt": "C:\\Users\\user\\project\\src\\app.py はどの種類のパス？", "options": ["相対パス", "絶対パス", "拡張子", "コマンド"], "answer": 1, "hint": "ドライブ名から場所を示しているか確認しましょう。", "explanation": "C:から始まるこの例は絶対パスです。"},
                {"prompt": "現在位置が C:\\Users\\user\\project のとき、src内のapp.pyを指す相対パスは？", "options": ["src\\app.py", "C:\\src\\app.py", "..\\src\\app.py", "app.py\\src"], "answer": 0, "hint": "現在位置はすでにprojectです。そこから下の階層をたどります。", "explanation": "projectからは src\\app.py で指せます。"},
                {"prompt": "相対パスの意味が変わる主な理由は？", "options": ["CPUの名称", "現在位置の変更", "画面の色", "ファイルの拡張子"], "answer": 1, "hint": "どこを起点にして場所を読むかを考えましょう。", "explanation": "相対パスは現在位置を起点とするため、現在位置に依存します。"},
                {"prompt": "相対パスの .. は何を表す？", "options": ["同じフォルダ", "一つ上のフォルダ", "SSD", "Webサイト"], "answer": 1, "hint": "フォルダ階層を一段戻る記号です。", "explanation": ".. は一つ上のフォルダを示します。"},
                {"prompt": "現在位置が project\\src のとき、project内のREADME.mdを指す相対パスは？", "options": ["src\\README.md", "..\\README.md", "C:\\README.md", "README.md\\.."], "answer": 1, "hint": "まず一つ上のフォルダへ戻る必要があります。", "explanation": "..\\README.md で親フォルダにあるREADME.mdを指せます。"},
                {"prompt": "現在位置が project\\src で、同じフォルダの app.py を指す書き方は？", "options": [".\\app.py", "..\\app.py", "src\\app.py", "app.py\\.."], "answer": 0, "hint": ". は今いるフォルダを示します。", "explanation": ".\\app.py は現在位置にあるapp.pyを指します。"},
            ],
        },
        {
            "id": "processes",
            "title": "プログラムとプロセス",
            "summary": "保存されたプログラムと、それを実行している活動は別のものです。",
            "questions": [
                {"prompt": "プログラムとは何？", "options": ["画面の色", "処理手順を記したもの", "必ず実行中の活動", "入力装置"], "answer": 1, "hint": "実行する前にもファイルとして保存できるものです。", "explanation": "プログラムは処理手順です。"},
                {"prompt": "プロセスを最もよく説明するのは？", "options": ["保存された画像", "ディレクトリの別名", "実行中のプログラムに関係する活動単位", "拡張子"], "answer": 2, "hint": "保存だけでなく、いま動いている状態に注目しましょう。", "explanation": "プロセスは実行中のプログラムに関係する活動単位です。"},
                {"prompt": "保存済みの app.py をまだ起動していない場合、正しい説明は？", "options": ["ファイルはあるが、その実行プロセスはまだない", "必ずプロセスが動いている", "OSが存在しない", "CPUが保存先になる"], "answer": 0, "hint": "保存と実行は別の段階です。", "explanation": "ファイルの保存だけでは、そのプログラムの実行プロセスは始まりません。"},
                {"prompt": "プロセスを管理する基本ソフトは？", "options": ["Chrome", "OS", "写真ファイル", "キーボード"], "answer": 1, "hint": "計算資源や実行中のプログラムを管理する基本ソフトです。", "explanation": "OSがプロセスを管理します。"},
                {"prompt": "「プログラムを実行する」に近い説明は？", "options": ["ファイル名を変えるだけ", "処理手順を動かして処理を行わせる", "写真を長期保存するだけ", "電源を切ること"], "answer": 1, "hint": "保存された手順を実際に動かすことです。", "explanation": "実行すると、プログラムの手順に沿った処理が始まります。"},
                {"prompt": "同じプログラムを二回起動した場合、プロセスについてあり得るのは？", "options": ["必ずファイルが二つに複製される", "同じコードから複数のプロセスができる", "OSはどちらも管理しない", "CPUがストレージに変わる"], "answer": 1, "hint": "保存された手順の数と、実行中の活動単位の数は同じとは限りません。", "explanation": "同じプログラムから複数のプロセスが存在し得ます。"},
            ],
        },
        {
            "id": "interfaces",
            "title": "GUI・CLI・ターミナル",
            "summary": "画面のボタンで操作する方法と、文字のコマンドで操作する方法があります。",
            "questions": [
                {"prompt": "マウスでウィンドウやボタンを操作する方式は？", "options": ["CLI", "GUI", "CPU", "RAM"], "answer": 1, "hint": "図形的な画面要素を使う方式です。", "explanation": "GUIはボタンやウィンドウを使う操作方式です。"},
                {"prompt": "git status のように文字を入力して操作する方式は？", "options": ["GUI", "SSD", "CLI", "画像形式"], "answer": 2, "hint": "コマンドラインの略語を探しましょう。", "explanation": "CLIでは文字のコマンドを入力します。"},
                {"prompt": "ターミナルの説明として適切なのは？", "options": ["コマンドライン環境を使うための画面・アプリ", "常にPowerShellと完全に同じもの", "画像ファイルの形式", "CPUの一部"], "answer": 0, "hint": "コマンドを入力する場所に注目しましょう。", "explanation": "ターミナルはコマンドライン環境を使う画面・アプリです。"},
                {"prompt": "PowerShellの説明として適切なのは？", "options": ["入力装置の種類", "コマンドラインシェル兼スクリプト言語", "画像形式", "ストレージの種類"], "answer": 1, "hint": "入力されたコマンドを解釈する側です。", "explanation": "PowerShellはシェルであり、スクリプト言語でもあります。"},
                {"prompt": "GUIとCLIの使い分けで適切なのは？", "options": ["どちらも同じ画面だけを使う", "CLIでは文字を入力できない", "目的に応じて両方を使える", "GUIを使うとOSが不要"], "answer": 2, "hint": "片方だけに限定する必要はありません。", "explanation": "目で見ながらの操作と、決まったコマンドの操作を目的に応じて使い分けます。"},
                {"prompt": "ターミナルで git status と入力した場合、コマンドを解釈する役割を担うのは？", "options": ["ディスプレイそのもの", "シェル", "SSD", "拡張子"], "answer": 1, "hint": "入力する画面と、入力内容を解釈するソフトを分けましょう。", "explanation": "PowerShellなどのシェルがコマンドを解釈します。"},
            ],
        },
    ],
    "boss": [
        {"type": "true_false", "prompt": "SSDに保存したファイルは、通常、電源を切るとRAMの作業中データと同じように消える。", "answer": "false", "hint": "一時保持と長期保存を区別しましょう。", "explanation": "SSDは長期保存のストレージで、一般的なRAMは揮発性です。"},
        {"type": "term", "prompt": "アプリが利用するCPU・メモリ・ファイルや実行中の活動を管理する基本ソフトの総称は？", "answer": "OS", "accepted_answers": ["OS", "Operating System", "オペレーティングシステム"], "hint": "Windows、macOS、Linuxがこの分類に入ります。", "explanation": "OS（Operating System）がコンピュータの資源を管理します。"},
        {"type": "true_false", "prompt": "photo.jpg の名前を photo.txt に変えるだけで、画像データは文章データへ変換される。", "answer": "false", "hint": "ファイル名の目印と、内部データの形式は別です。", "explanation": "拡張子の変更だけでは内部データ形式は変わりません。"},
        {"type": "true_false", "prompt": "project\\src はフォルダ、app.py はファイルで、.py はそのファイル名の拡張子である。", "answer": "true", "hint": "データの単位、整理する入れ物、名前の末尾を区別しましょう。", "explanation": "srcはフォルダ、app.pyはファイル、.pyは拡張子です。"},
        {"type": "application", "prompt": "現在位置は C:\\Users\\user\\project。C:\\Users\\user\\project\\src\\app.py を指す相対パスは？", "options": ["src\\app.py", "C:\\Users\\user\\project\\src\\app.py", "..\\src\\app.py", "app.py\\src"], "answer": 0, "hint": "現在位置から、下のsrcフォルダへ進みます。", "explanation": "現在位置がprojectなら src\\app.py で指せます。"},
        {"type": "term", "prompt": "保存されたプログラムを実行したとき、その実行に関係する活動単位を何という？", "answer": "プロセス", "accepted_answers": ["プロセス", "process"], "hint": "保存された手順ではなく、動いている状態の名前です。", "explanation": "実行中のプログラムに関係する活動単位はプロセスです。"},
        {"type": "true_false", "prompt": "WindowsはOS、ChromeとVS Codeはアプリケーションである。", "answer": "true", "hint": "全体を管理する基本ソフトと、特定の作業をするソフトを区別しましょう。", "explanation": "WindowsはOS、ChromeとVS Codeはアプリです。"},
        {"type": "application", "prompt": "SSD上のapp.pyをPowerShellから実行したとき、保存先・操作方式・実行中の活動単位・管理する基本ソフトの組み合わせは？", "options": ["メモリ・GUI・ファイル・Chrome", "ストレージ・CLI・プロセス・OS", "CPU・GUI・フォルダ・SSD", "ストレージ・GUI・拡張子・Chrome"], "answer": 1, "hint": "保存、操作、実行中、管理者の4つの役割を順に分けて考えましょう。", "explanation": "SSDはストレージ、PowerShell操作はCLI、実行中はプロセス、管理する基本ソフトはOSです。"},
        {"type": "term", "prompt": "CLIでコマンドを解釈し、Windowsで使えるシェル兼スクリプト言語の名前は？", "answer": "PowerShell", "hint": "コマンドを入力する画面そのものではなく、その中で働く仕組みです。", "explanation": "PowerShellはコマンドラインシェル兼スクリプト言語です。"},
        {"type": "true_false", "prompt": "現在位置が変わっても、相対パス src\\app.py は必ず同じファイルを指す。", "answer": "false", "hint": "相対パスがどこを起点にするかを確認しましょう。", "explanation": "相対パスは現在位置に依存します。"},
        {"type": "application", "prompt": "現在位置が C:\\Users\\user\\project\\src。親フォルダのREADME.mdを指す相対パスは？", "options": ["src\\README.md", "..\\README.md", "README.md\\..", "C:\\README.md"], "answer": 1, "hint": "一つ上のフォルダを示す記号を使います。", "explanation": "..\\README.md で親フォルダのファイルを指せます。"},
        {"type": "true_false", "prompt": "ターミナルはコマンドライン環境を使う画面・アプリで、PowerShellはそこで使えるシェルの一つである。", "answer": "true", "hint": "入力する場所と、コマンドを解釈する仕組みは別です。", "explanation": "ターミナルとPowerShellは役割が異なります。"},
        {"type": "application", "prompt": "キーボードで文字を入力して文書アプリに表示し、その後SSDへ保存した。役割の組み合わせで正しいものは？", "options": ["キーボードは入力、ディスプレイは出力、SSDは長期保存", "キーボードは出力、ディスプレイは入力、SSDは計算", "キーボードは保存、ディスプレイはOS、SSDは一時保持", "すべてCPUと同じ役割"], "answer": 0, "hint": "情報が人から入る方向、見える方向、電源OFF後にも残す場所を分けましょう。", "explanation": "キーボードで入力し、ディスプレイへ出力し、SSDへ長期保存します。"},
        {"type": "application", "prompt": "PowerShellで python -m src.app を入力して起動した。実行までの説明として最も適切なのは？", "options": ["ターミナルがPythonコードを直接CPU命令として解釈し、OSは使われない", "PowerShellがコマンドを解釈し、OSが実行を管理し、必要な情報をメモリで扱い、CPUが命令を処理する", "SSDが実行中のプロセスそのものになり、RAMは長期保存だけを行う", "コマンドを入力するとファイルの拡張子が変わり、アプリは起動しない"], "answer": 1, "hint": "コマンドを扱うもの、実行を管理するもの、一時保持するもの、処理するものを順に考えましょう。", "explanation": "シェル・OS・メモリ・CPUがそれぞれ異なる役割を担い、実行中はプロセスとして管理されます。"},
    ],
}

# 問題データと本文を分け、今後の教材追加でも画面側は変えずに済むようにする。
for lesson in COMPUTER_OS_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])
