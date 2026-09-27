"""Build画面と保存・実行API。利用者コードはこのプロセスでは実行しない。"""

import secrets
import threading

from flask import Blueprint, current_app, jsonify, render_template, request, session

from src.build_ai import ask_guide
from src.build_ai_context import safe_history, secret_values
from src.build_preview import local_path, make_preview
from src.build_runtime import DockerRuntime, runtime_status, validate_runtime_result
from src.build_store import BuildStore, public_project

build = Blueprint("build", __name__, url_prefix="/build")
run_lock = threading.Lock()


def store():
    return BuildStore(current_app.instance_path)


@build.before_request
def protect_build():
    # ブラウザーの外部サイトから、ローカルのコード保存・実行を指示させない。
    if request.method == "POST":
        request.max_content_length = 800_000
        if request.content_length and request.content_length > 800_000:
            return jsonify(error="送信データが大きすぎます。"), 413
        token = session.get("build_csrf", "")
        supplied = request.headers.get("X-Build-CSRF", "")
        if not token or not secrets.compare_digest(token.encode(), supplied.encode()):
            return jsonify(error="画面を再読み込みしてください。"), 403
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            return jsonify(error="この画面から操作してください。"), 403
        if not request.is_json:
            return jsonify(error="JSON形式で送信してください。"), 415
    if "build_owner" not in session:
        session["build_owner"] = secrets.token_hex(24)
        session["build_csrf"] = secrets.token_hex(24)


@build.after_request
def build_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@build.errorhandler(ValueError)
def invalid_request(error):
    return jsonify(error=str(error)), 400


@build.errorhandler(413)
def request_too_large(error):
    return jsonify(error="送信データが大きすぎます。"), 413


@build.errorhandler(FileExistsError)
def stale_request(error):
    return jsonify(error=str(error)), 409


@build.errorhandler(LookupError)
def missing_project(error):
    return jsonify(error="プロジェクトが見つかりません。"), 404


def payload():
    data = request.get_json()
    if not isinstance(data, dict):
        raise ValueError("送信形式を確認してください。")
    return data


def get_project(project_id):
    return store().get(session["build_owner"], project_id)


def capabilities():
    return runtime_status(current_app.config["BUILD_DOCKER_ENABLED"])


@build.get("/")
def home():
    database = store()
    projects = database.list_projects(session["build_owner"])
    if not projects:
        project = database.create(session["build_owner"], "わたしのアプリ")
        projects = database.list_projects(session["build_owner"])
    else:
        selected = request.args.get("project", session.get("build_project", projects[0]["id"]))
        project = database.get(session["build_owner"], selected)
    session["build_project"] = project["id"]
    initial = {"project": public_project(project), "projects": projects,
               "csrf": session["build_csrf"], "runtime": capabilities()}
    return render_template("build.html", initial=initial,
                           ai_label=current_app.config["BUILD_AI_LABEL"],
                           ai_connected=current_app.config.get("BUILD_AI_PROVIDER") is not None)


@build.post("/projects")
def create_project():
    project = store().create(session["build_owner"], payload().get("name"))
    session["build_project"] = project["id"]
    return jsonify(project=public_project(project)), 201


@build.get("/projects/<project_id>")
def load_project(project_id):
    project = get_project(project_id)
    session["build_project"] = project_id
    return jsonify(project=public_project(project))


@build.post("/projects/<project_id>/save")
def save_project(project_id):
    get_project(project_id)
    project = store().save(session["build_owner"], project_id, payload())
    return jsonify(project=public_project(project))


@build.post("/projects/<project_id>/run")
def run_project(project_id):
    project = get_project(project_id)
    data = payload()
    if data.get("revision") != project["revision"]:
        raise FileExistsError("保存したコードが更新されています。再読み込みしてください。")
    mode = data.get("mode", "html")
    path = local_path(data.get("path", "/"))
    method = data.get("method", "GET")
    fields = data.get("data", {})
    if not isinstance(method, str) or method not in {"GET", "POST"} or not isinstance(fields, dict) or len(fields) > 30:
        raise ValueError("プレビューのリクエスト形式を確認してください。")
    if any(not isinstance(k, str) or not isinstance(v, str) or len(k) > 100 or len(v) > 5000 for k, v in fields.items()):
        raise ValueError("フォーム入力が大きすぎます。")
    if mode == "html":
        if method != "GET" or fields:
            raise ValueError("フォームのサーバー処理にはFlaskモードが必要です。入力内容は送信していません。")
        entry = data.get("entry", "templates/index.html")
        if not isinstance(entry, str) or not entry.endswith(".html") or entry not in project["files"]:
            raise ValueError("プレビューするHTMLファイルを選択してください。")
        if path != "/":
            candidate = path.split("?")[0].lstrip("/")
            if not candidate.endswith(".html") or candidate not in project["files"]:
                raise ValueError("このパスはHTMLファイルではありません。Routeの実行にはFlaskモードが必要です。")
            entry = candidate
        preview_path = "/" + entry
        result = {"html": project["files"][entry], "status": 200,
                  "logs": f"HTML/CSS: {entry}\nPython・Jinja・利用者のJavaScriptは実行していません。"}
    elif mode == "flask":
        runtime_info = capabilities()
        if not runtime_info["available"]:
            raise ValueError("Flask隔離実行が未設定です。HTML/CSSモードで確認できます。設定はdocs/BUILD.mdを参照してください。")
        if "app.py" not in project["files"]:
            raise ValueError("Flaskモードにはapp.pyが必要です。")
        if not run_lock.acquire(blocking=False):
            return jsonify(error="別の実行が進行中です。少し待って再実行してください。"), 409
        try:
            runtime = current_app.config.get("BUILD_RUNTIME") or DockerRuntime(runtime_info["endpoint"])
            result = validate_runtime_result(runtime.run(project, path, method, fields))
            store().save_runtime(session["build_owner"], project_id, project["revision"], result["state"])
        finally:
            run_lock.release()
        preview_path = path
    else:
        raise ValueError("実行モードを選択してください。")
    preview = make_preview(result["html"], project["files"], preview_path)
    return jsonify(**preview, status=result["status"], logs=result["logs"], mode=mode)


@build.post("/projects/<project_id>/chat")
def chat(project_id):
    project = get_project(project_id)
    data = payload()
    question = data.get("question", "")
    active_file = data.get("active_file", project["active_file"])
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 1500:
        raise ValueError("質問は1〜1500文字で入力してください。")
    if not isinstance(active_file, str) or active_file not in project["files"]:
        raise ValueError("ファイルを選択してください。")
    secrets = secret_values(project, (current_app.secret_key, session.get("build_csrf", "")))
    reply = ask_guide(current_app.config.get("BUILD_AI_PROVIDER"), project, active_file, question,
                      preview=data.get("preview"), secrets=secrets)
    safe_question = reply.pop("question")
    history = safe_history(project["chat"], secrets) + [{"role": "user", "text": safe_question}, {"role": "assistant", "text": reply["answer"]}]
    store().save_chat(session["build_owner"], project_id, history)
    return jsonify(**reply, chat=history[-20:])


@build.post("/projects/<project_id>/advice")
def advice(project_id):
    project = get_project(project_id)
    active_file = payload().get("active_file", project["active_file"])
    if not isinstance(active_file, str) or active_file not in project["files"]:
        raise ValueError("ファイルを選択してください。")
    return jsonify(ask_guide(None, project, active_file, "次に確認すること"))
