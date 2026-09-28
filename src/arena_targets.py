"""Dockerへ渡す、ゲーム専用の架空Flaskターゲット。ホストではimport・実行しない。"""

def target_files(scenario, marker):
    settings = {"family": scenario["family"], "difficulty": scenario["difficulty"],
                "title": scenario["title"], "marker": marker}
    return {"app.py": "SETTINGS = " + repr(settings) + "\n" + TARGET_CODE}


TARGET_CODE = '''
import os
import sqlite3
from flask import Flask, request, session
app = Flask(__name__)
app.secret_key = os.environ["BUILD_APP_SECRET"]
hard = SETTINGS["difficulty"] == "hard"
record_id = "7317" if hard else "102"

def catalog():
    family = SETTINGS["family"]
    if family == "records":
        return "公開記録: GET /records?id=101\\nチーム一覧: public=101 / internal=" + record_id
    if family == "exports":
        return "出力API: GET /export または POST /export / 入力名scope: public, internal"
    if family == "search":
        return "検索API: GET /search / 入力名q（初期検索語: guide）"
    return "GET /status で稼働情報を確認できます。"

@app.before_request
def exercise_session():
    if hard and request.path not in ("/", "/connect") and not session.get("connected"):
        return "演習セッションが必要です。トップの案内を確認してください。", 403

@app.get("/")
def index():
    if hard:
        return SETTINGS["title"] + "\\n演習接続: POST /connect / 入力team=guest。その後 GET /catalog。"
    return SETTINGS["title"] + "\\n" + catalog()

@app.post("/connect")
def connect():
    if request.form.get("team") != "guest":
        return "演習チームが違います。", 400
    session["connected"] = True
    return "演習セッションを開始しました。GET /catalog"

@app.get("/catalog")
def directory():
    if hard:
        session["catalog_seen"] = True
    return catalog()

@app.before_request
def route_discovery():
    if hard and request.path not in ("/", "/connect", "/catalog") and not session.get("catalog_seen"):
        return "接続後のAPI案内を先に取得してください。", 403

@app.get("/records")
def records():
    if SETTINGS["family"] != "records": return "Not found", 404
    if request.args.get("id") == record_id:
        return "INTERNAL / " + SETTINGS["marker"]
    if request.args.get("id") == "101": return "PUBLIC / 公開記録"
    return "記録がありません。", 404

@app.route("/export", methods=["GET", "POST"])
def export():
    if SETTINGS["family"] != "exports": return "Not found", 404
    if request.method == "GET": return "内部出力は権限が必要です。", 403
    if request.form.get("scope") == "internal": return "INTERNAL / " + SETTINGS["marker"]
    return "公開用の帳票です。scopeを指定できます。"

@app.get("/search")
def search():
    if SETTINGS["family"] != "search": return "Not found", 404
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE docs (title TEXT, public INTEGER)")
        db.executemany("INSERT INTO docs VALUES (?, ?)", [("guide", 1), (SETTINGS["marker"], 0)])
        # 意図的な弱点。ゲームの使い捨てコンテナー内の教材以外へ転用しない。
        query = "SELECT title FROM docs WHERE public=1 AND title='" + request.args.get("q", "guide") + "'"
        return "\\n".join(row[0] for row in db.execute(query)) or "検索結果なし"
    except sqlite3.Error:
        return "検索条件をSQLとして解析できませんでした。", 400
    finally:
        db.close()

@app.get("/status")
def status():
    if SETTINGS["family"] != "support": return "Not found", 404
    return "稼働中 / 詳細窓口: GET /support / パラメーターview: summary, full"

@app.get("/support")
def support():
    if SETTINGS["family"] != "support": return "Not found", 404
    if request.args.get("view") == "full": return "管理者向け診断 / " + SETTINGS["marker"]
    return "稼働中 / summary"
'''
