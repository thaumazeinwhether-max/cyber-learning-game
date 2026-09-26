"""正式第8訓練の問題。SQLは画面上で読むだけでDBへ実行しない。"""

from src.database_sql_chapters import CHAPTERS
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


DATABASE_SQL_COURSE = {
    "title": "データベース・SQL基礎訓練",
    "description": "Webアプリのデータ保存、RDBの構造、基本SQLを学ぶ正式第8訓練。",
    "question_mode": "choice",
    "curriculum_number": 8,
    "lesson_label": "UNIT",
    "boss_name": "DATA VAULT",
    "lessons": [
        {"id": "database", "title": "データベースとは", "summary": "保存と検索をWebアプリへつなげます。", "questions": [
            choice("利用者が次回アクセスしたときにも名前を表示したい。必要な考え方は？", "持続的な保存", "Pythonの変数だけに置く", "CSSの色を変える", "HTTP 200を返すだけ", "次のRequestでも使う情報は持続的に保存します。"),
            choice("DBの説明として適切なのは？", "データを整理し保存・検索・更新する仕組み", "ブラウザーの見た目だけを変えるもの", "CPUを置き換えるもの", "すべてのファイルを不要にするもの", "DBは関連する記録を整理して扱います。"),
            choice("少数の文章を保存するだけのときは？", "通常のファイルで足りる場合もある", "必ず大規模DBが必要", "変数だけで永続保存できる", "保存は一切不要", "用途と件数に応じて方法を選びます。"),
            choice("DBMSが主に行うことは？", "DBの管理", "HTMLの装飾", "HTTP Requestの送信だけ", "画像を表示するだけ", "DBMSは保存・取得などの操作を管理するソフトウェアです。"),
        ]},
        {"id": "rdb", "title": "RDBとテーブル", "summary": "表とその関係を学びます。", "questions": [
            choice("RDBとDBの関係は？", "RDBはDBの一種類", "完全な同義語", "RDBは画像形式", "DBはRDBの一種類だけ", "RDBは関係モデルに基づくデータベースです。"),
            choice("利用者と投稿を分ける自然な構成は？", "usersとpostsを別テーブルにする", "全投稿をCSSへ入れる", "1投稿ごとにOSを作る", "表を一切使わない", "異なる種類の記録を分け、キーで関連付けます。"),
            choice("RDBと表計算ソフトについて適切なのは？", "見た目は似ても制約・操作方法が異なる", "完全に同じ", "RDBには行がない", "表計算ソフトには列がない", "RDBはSQLやキーなどで記録を管理します。"),
            choice("SQLiteやMySQLは何の例？", "RDBを扱う製品", "Pythonの比較演算子", "HTTPメソッド", "画像ファイル形式", "どちらも関係データベースを扱う製品です。"),
        ]},
        {"id": "rows", "title": "row・column・data type", "summary": "表の一件・属性・型を区別します。", "questions": [
            choice("usersの一人分の記録は？", "row", "column", "table全体", "data type", "rowは一件の記録です。"),
            choice("全利用者に共通するemailという属性は？", "column", "row", "DBMS", "commit", "columnは各記録の属性を表します。"),
            choice("id=2のBobのemailを読むには？", "id=2の行のemail列", "emailという行のid=2列", "users以外のOS", "全列を削除する", "行で一件を選び、その行の列の値を読みます。"),
            choice("計算に使う整数値の型の例は？", "INTEGER", "TEXTだけ", "HTML", "HTTP", "INTEGERは整数値の型です。"),
        ]},
        {"id": "primary_key", "title": "primary key", "summary": "一件を確実に識別します。", "questions": [
            choice("主キーの目的は？", "各行を一意に識別する", "全行の名前を同じにする", "HTMLを作る", "通信先を決める", "主キーは行を区別する基準です。"),
            choice("同姓同名の二人を区別したい。適切なのは？", "重複しないidを主キーにする", "名前だけを使う", "メールを全部消す", "全員のidを1にする", "名前は重複や変更があり得ます。"),
            choice("主キーの値に求められる性質は？", "重複せずNULLでもない", "必ず重複する", "必ず空", "CSSに保存される", "主キーは一意で値を持ちます。"),
            choice("主キーidに欠番が出たら？", "一意性が保たれれば識別の役割は続く", "必ずDBを削除する", "全員同じidに直す", "名前を主キーに変える", "番号が連続することより、行ごとに一意であることが重要です。"),
        ]},
        {"id": "foreign_key", "title": "foreign keyとrelation", "summary": "別の表を安全に参照します。", "questions": [
            choice("posts.user_idがusers.idを指す場合、posts.user_idは？", "外部キー", "postsの主キーだけ", "SQL文の名前", "HTML要素", "外部キーは別テーブルのキーを参照します。"),
            choice("users一件にposts複数件が対応する関係は？", "一対多", "常に一対一", "関係なし", "全行が同じ", "一人の利用者が複数投稿を持てます。"),
            choice("参照整合性の考え方は？", "存在しない参照先を防ぐ", "全投稿の題名を同じにする", "投稿を画像へ変換する", "キーを必ず空にする", "有効な外部キー制約は参照先の存在を検査します。"),
            choice("posts.idとposts.user_idの違いは？", "前者は投稿自身、後者は利用者を指す", "どちらも利用者名", "前者だけがSQL", "完全に同じ役割", "自表の主キーと他表を指す外部キーは役割が異なります。"),
        ]},
        {"id": "select", "title": "SQLとSELECT", "summary": "必要な列を取得します。", "questions": [
            choice("SQLは何をする言語？", "RDBへ取得や変更を指示する", "CSSを着色する", "CPUそのもの", "Python専用の画像形式", "SQLはStructured Query Languageです。"),
            choice("このSQLの結果に含める列は？", "nameとemail", "idだけ", "全列", "列は返らない", "SELECTでnameとemailを指定しています。", "SELECT name, email FROM users;"),
            choice("FROM usersが示すものは？", "読むテーブル", "追加する画像", "画面の色", "HTTP Status", "FROMの後に取得元テーブルを指定します。"),
            choice("SELECT *の*が示すものは？", "対象テーブルの全列", "すべてのSQL操作", "すべてのDB", "一行だけ", "*はSELECT対象の全列です。"),
        ]},
        {"id": "where", "title": "WHERE", "summary": "条件で行を絞ります。", "questions": [
            choice("このSQLで対象になる行は？", "idが1の行", "全列を削除", "必ず全行", "nameが1の行", "WHERE id = 1で行を絞ります。", "SELECT name FROM users WHERE id = 1;"),
            choice("SQLで等しいことを表す記号は？", "=", "==だけ", ":=", "=>", "SQLの等値比較は=です。Pythonの==と区別します。"),
            choice("WHERE id = 1 AND name = 'Alice'は？", "両条件を満たす行", "どちらか一方だけ", "全行", "列名を変更", "ANDは両方を満たす行を選びます。"),
            choice("WHERE name = 'Alice'の結果数は？", "0件以上で複数件もあり得る", "必ず1件", "必ず0件", "必ず全件", "名前は一意とは限らないため複数件もあり得ます。"),
        ]},
        {"id": "insert", "title": "INSERT", "summary": "新しい行を追加します。", "questions": [
            choice("INSERTの主な効果は？", "新しい行を追加", "既存行を読むだけ", "表を必ず削除", "HTMLを装飾", "INSERTは記録の追加です。"),
            choice("このSQLでemail列へ入る値は？", "a@example.com", "Alice", "users", "id", "VALUESの二番目は列一覧の二番目emailに対応します。", "INSERT INTO users (name, email) VALUES ('Alice', 'a@example.com');"),
            choice("id列をINSERTで省けるのはどんな場合？", "自動採番などテーブル設計で許される場合", "常に省ける", "SELECTを先にした場合だけ", "HTMLで定義した場合", "必要な列と既定値は表の設計に依存します。"),
            choice("列とVALUESの対応がずれると？", "意図した値が違う列に入るか失敗する", "自動で意味から修正", "SELECTに変わる", "必ず行が削除される", "値は列の指定順に対応します。"),
        ]},
        {"id": "update_delete", "title": "UPDATE・DELETE", "summary": "既存行を変更・削除します。", "questions": [
            choice("このSQLの操作は？", "id=1のnameを変える", "新しい行を追加", "全行のidを変える", "表を作る", "UPDATEのSETで値を変え、WHEREで対象を絞ります。", "UPDATE users SET name = 'Alice Smith' WHERE id = 1;"),
            choice("DELETE FROM users WHERE id = 1は？", "id=1の行を削除", "id=1の列を追加", "全列を取得", "nameを更新", "DELETEは行を消し、WHEREは対象を絞ります。"),
            choice("UPDATEでWHEREを書かない場合は？", "複数行・全行が対象になり得る", "自動で一件だけ選ぶ", "必ず何もしない", "SELECTに変わる", "WHEREがなければ対象行を絞れません。"),
            choice("DELETEでWHERE name='Alice'としたときの注意は？", "同名の複数行を消し得る", "必ず一行だけ", "全列を追加する", "値を更新する", "nameは一意とは限りません。"),
        ]},
        {"id": "web_db", "title": "Webアプリとデータベース", "summary": "Requestから保存・表示までを統合します。", "questions": [
            choice("画面表示までの基本順は？", "Request→Flask→DB→Template→Response", "DB→ブラウザーが直接SQL実行", "CSS→DB→CPU停止", "Response→Requestだけ", "FlaskがDBを利用し結果をTemplateへ渡します。"),
            choice("利用者の入力をSQLに渡す安全な考え方は？", "文と値を分けて渡す", "文字列を直接連結する", "入力確認は一切しない", "権限を全員に与える", "パラメータ化クエリなどで値をSQL構造と分けます。"),
            choice("DBの役割は？", "記録の保存・検索・更新", "HTMLの色を決めるだけ", "ブラウザー表示そのもの", "RouteのURL生成だけ", "DBはデータを持続的に扱います。"),
            choice("パラメータ化クエリを使えば？", "SQLへの値の受け渡しを安全にし、別の確認も必要", "認証と権限がすべて不要", "入力が必ず正しい", "テストが不要", "安全な値の受け渡しと入力確認・権限確認は別です。"),
        ]},
    ],
    "boss": [
        true_false("DBは保存だけに使い、検索や更新には使えない。", "false", "DBは保存・検索・更新・削除を扱います。"),
        term("RDBで一件の記録を表す横方向の単位は？英語で答えてください。", "row", "rowは一件の記録で、recordとも呼ばれます。", "record"),
        choice("同名の利用者を区別し、投稿から参照したい。usersとpostsの適切な列は？", "users.idを主キー、posts.user_idを外部キー", "両方のnameだけ", "両表に同じtitleだけ", "主キーを作らない", "主キーが利用者を一意に識別し、外部キーが参照します。"),
        true_false("外部キー制約を適切に設定・有効化すれば、存在しない参照先を防げる。", "true", "参照整合性は表間の矛盾を減らします。"),
        choice("usersからnameだけを取得するSQLの読み方は？", "SELECT name FROM users", "INSERT name FROM users", "DELETE name FROM users", "UPDATE name FROM users", "SELECTが取得列、FROMが対象テーブルです。", "SELECT name FROM users;"),
        choice("このSQLが返す行は？", "id=2に合う行", "すべての行", "新しい行", "id列を削除", "WHEREが行を絞ります。", "SELECT name FROM users WHERE id = 2;"),
        term("SELECT文で行を条件により絞るキーワードは？", "WHERE", "WHEREは行を絞ります。SELECTは列を指定します。", "where"),
        choice("このSQLの効果は？", "usersへ一件の行を追加", "既存の行を削除", "全件表示", "name列を削除", "INSERT INTOとVALUESが新しい行の列・値を対応付けます。", "INSERT INTO users (name, email) VALUES ('Bob', 'b@example.com');"),
        true_false("WHEREを省いたUPDATEは、自動的に主キーが最小の一件だけを変更する。", "false", "条件がなければ複数行、場合によっては全行を変更します。"),
        choice("このSQLの結果として適切なのは？", "id=1の行が削除対象", "name列だけ削除", "全行に新規値を追加", "すべての表を消す", "DELETE FROMは行の削除、WHEREは対象条件です。", "DELETE FROM users WHERE id = 1;"),
        choice("ブラウザーの表示までの役割の組み合わせは？", "FlaskがDBへ問い合わせ、TemplateがHTMLを作る", "DBがブラウザーのHTMLを直接描く", "ブラウザーがDBの全権限を持つ", "CSSがSQLを採点する", "RouteのPython処理がDBを利用し、結果をTemplateへ渡します。"),
        true_false("ユーザー入力をSQL文字列へ直接連結するより、値を分けて渡す仕組みを使う。", "true", "パラメータ化クエリ等は値をSQL構造と分離します。"),
        choice("users(id=1, name='Alice')とposts(id=10, user_id=1)がある。正しい読み方は？", "投稿10は利用者Aliceを参照する", "投稿10自身の主キーは1", "利用者Aliceの主キーは10", "posts.user_idはHTML", "posts.user_idがusers.idを参照します。"),
        choice("フォームから受け取った利用者IDで本人の名前だけを表示する。Requestから表示まで適切な流れは？", "入力と閲覧権限を確認→固定したSELECT/WHEREへIDを値として渡す→Templateへ結果を渡す", "IDが整数なら権限確認を省き、SQL文字列へ直接連結する", "まず全行を取得してからブラウザー側だけで本人分を選ぶ", "WHEREを使う代わりにDBへ利用者IDを表名として渡す", "Requestの値と権限を確認し、WHEREの値はSQL構造と分離して渡し、結果だけを表示します。"),
    ],
}

for lesson in DATABASE_SQL_COURSE["lessons"]:
    lesson.update(CHAPTERS[lesson["id"]])

arrange_choices(DATABASE_SQL_COURSE)

for question in (
    [item for lesson in DATABASE_SQL_COURSE["lessons"] for item in lesson["questions"]]
    + DATABASE_SQL_COURSE["boss"]
):
    if "options" in question:
        right = question["options"][question["answer"]]
        question["wrong_explanations"] = {
            str(index): f"「{option}」はこの場面の正解ではありません。{question['explanation']} 正しい選択肢は「{right}」です。"
            for index, option in enumerate(question["options"]) if index != question["answer"]
        }
