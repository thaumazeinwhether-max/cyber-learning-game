"""編集できる出発点。テーマや機能は利用者が自由に書き換える。"""

STARTER_FILES = {
    "app.py": '''import os
import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
# Buildの隔離実行環境が、プロジェクト専用の秘密鍵を設定します。
app.secret_key = os.environ.get("BUILD_APP_SECRET")


def connect_db():
    db = sqlite3.connect("data/app.sqlite3")
    db.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, body TEXT)")
    return db


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            with connect_db() as db:
                db.execute("INSERT INTO entries (body) VALUES (?)", (body,))
            session["message"] = "保存しました"
            app.logger.info("entry saved")
        return redirect("/")

    with connect_db() as db:
        entries = db.execute("SELECT body FROM entries ORDER BY id DESC").fetchall()
    return render_template("index.html", entries=entries,
                           message=session.pop("message", ""))
''',
    "templates/index.html": '''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>わたしのアプリ</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main class="card">
    <p class="label">MY FIRST APPLICATION</p>
    <h1>わたしのアプリ</h1>
    <p>ここから、あなたのアイデアを形にしましょう。</p>
    <form method="post" action="/">
      <label for="body">残しておきたいこと</label>
      <input id="body" name="body" required maxlength="500">
      <button type="submit">記録する</button>
    </form>
    <!-- 以下のJinja部分はFlask実行モードで動きます。 -->
    <p>{{ message }}</p>
    <ul>
      {% for entry in entries %}
      <li>{{ entry[0] }}</li>
      {% endfor %}
    </ul>
  </main>
</body>
</html>
''',
    "static/style.css": '''body { margin: 0; padding: 24px; background: #edf4f7; color: #153447;
       font-family: system-ui, sans-serif; line-height: 1.7; }
.card { max-width: 560px; margin: 0 auto; padding: 24px; background: white;
        border: 1px solid #c8dce5; border-radius: 16px; }
.label { color: #26798d; font-size: 12px; letter-spacing: 2px; }
h1 { font-size: 28px; }
form { display: grid; gap: 10px; }
input, button { padding: 10px; font: inherit; border: 1px solid #83aabb; border-radius: 6px; }
button { background: #176c85; color: white; cursor: pointer; }
''',
    "static/app.js": '''// JavaScriptもここに保存できます。
// 初期版の保護プレビューでは利用者のJavaScriptは実行しません。
// DOM操作などのコードを書き、将来の実行環境へ引き継げます。
''',
    "schema.sql": '''-- データ保存を設計するときのメモ。RUNで自動実行はしません。
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    body TEXT
);
''',
    "README.md": '''# わたしのアプリ

どんな人が、何のために使うアプリにするかを書いてみましょう。

- app.py: Flaskの処理。ルート、入力、DB、Session、ログ。
- templates/index.html: 画面の構造。
- static/style.css: 色やレイアウト。
- static/app.js: JavaScriptの作業用ファイル（初期版プレビューでは実行しません）。
- schema.sql: DB設計のメモ。
- data/app.sqlite3: Flask実行で作るDB。コードと別に自動保存します。

HTML/CSSモードは画面の見た目を確認します。PythonやJinjaは動きません。
Flaskモードには、管理者が用意したローカルの隔離実行環境が必要です。
''',
}
