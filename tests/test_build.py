"""Buildの保存、プレビューの境界、AI未接続時の動作を確認する。"""

import base64
import io
import json
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from src.app import create_app
from src.build_preview import local_path, make_preview
from src.build_runtime import container_command, validate_runtime_result
from src.build_store import BuildStore


@pytest.mark.parametrize("scenario", ["post_then_run", "changed_routes", "navigation", "save_only", "html_mode",
                                      "chat_flow", "chat_failure", "chat_rendering"])
def test_run_button_and_preview_navigation(scenario):
    node = shutil.which("node")
    assert node, "Buildのブラウザー側回帰テストにはNode.jsが必要です。"
    result = subprocess.run([node, str(Path(__file__).with_name("build_run_checks.cjs")), scenario],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture
def workspace():
    root = (Path(__file__).parents[1] / ".pytest_cache").resolve()
    directory = root / ("build_" + uuid.uuid4().hex)
    directory.mkdir(parents=True)
    yield directory
    assert directory.resolve().is_relative_to(root)
    shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture
def setup(workspace, monkeypatch):
    monkeypatch.delenv("BUILD_DOCKER_ENABLED", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = create_app(workspace)
    app.config["TESTING"] = True
    client = app.test_client()
    response = client.get("/build/")
    assert response.status_code == 200
    with client.session_transaction() as browser:
        headers = {"X-Build-CSRF": browser["build_csrf"]}
        owner = browser["build_owner"]
        project_id = browser["build_project"]
    project = client.get(f"/build/projects/{project_id}").json["project"]
    return app, client, headers, owner, project


def save(client, headers, project):
    return client.post(f'/build/projects/{project["id"]}/save', headers=headers, json=project)


def run(client, headers, project, **options):
    return client.post(f'/build/projects/{project["id"]}/run', headers=headers,
                       json={"revision": project["revision"], **options})


def test_build_ui_and_phase_navigation(setup):
    _, client, _, _, _ = setup
    page = client.get("/build/").get_data(as_text=True)
    for content in ("CODE", "PREVIEW", "NAVIGATOR", "AI CORE", "コードエディタ", "ローカルガイド", 'sandbox="allow-scripts allow-forms"'):
        assert content in page
    assert "allow-same-origin" not in page
    top = client.get("/").get_data(as_text=True)
    assert 'href="/build/"' in top
    assert "Attack &amp; Defend" in top and 'href="/arena/"' in top
    assert client.get("/learn/").status_code == 200
    assert client.get("/build/").headers["Cache-Control"] == "no-store"
    assert client.get("/build/").headers["X-Frame-Options"] == "DENY"


def test_save_files_active_file_and_restore_after_restart(setup, workspace):
    app, client, headers, owner, project = setup
    project["files"]["static/style.css"] = "body { color: navy; }"
    project["files"]["templates/about.html"] = "<h1>自由なテーマ</h1>"
    project["active_file"] = "templates/about.html"
    project["name"] = "学習日記"
    saved = save(client, headers, project).json["project"]
    assert saved["revision"] == project["revision"] + 1
    second_app = create_app(workspace)
    other_client = second_app.test_client()
    other_client.set_cookie("session", client.get_cookie("session").value)
    loaded = other_client.get(f'/build/projects/{project["id"]}').json["project"]
    assert loaded == saved
    assert app.secret_key == second_app.secret_key
    assert BuildStore(workspace).get(owner, project["id"])["files"]["static/style.css"] == "body { color: navy; }"


def test_projects_are_isolated_by_browser_session(setup):
    app, client, headers, _, project = setup
    stranger = app.test_client()
    stranger.get("/build/")
    with stranger.session_transaction() as browser:
        foreign_headers = {"X-Build-CSRF": browser["build_csrf"]}
    assert stranger.get(f'/build/projects/{project["id"]}').status_code == 404
    assert save(stranger, foreign_headers, project).status_code == 404
    assert run(stranger, foreign_headers, project).status_code == 404
    assert client.get(f'/build/projects/{project["id"]}').status_code == 200


def test_new_projects_keep_previous_code(setup):
    _, client, headers, _, project = setup
    response = client.post("/build/projects", headers=headers, json={"name": "別のアイデア"})
    assert response.status_code == 201
    assert response.json["project"]["id"] != project["id"]
    assert client.get(f'/build/projects/{project["id"]}').json["project"] == project


@pytest.mark.parametrize("path", ["../src/app.py", "C:/secret.txt", "/etc/passwd", "src//app.py", ".env", "data/app.sqlite3", "a\\b.py", "templates/../../app.py"])
def test_file_paths_cannot_escape_project_storage(setup, path):
    _, client, headers, _, project = setup
    project["files"][path] = "untrusted"
    assert save(client, headers, project).status_code == 400


def test_size_limits_and_invalid_payload(setup):
    _, client, headers, _, project = setup
    project["files"]["app.py"] = "x" * 100_001
    assert save(client, headers, project).status_code == 400
    assert client.post("/build/projects", headers=headers, json=[]).status_code == 400
    assert client.post("/build/projects", headers=headers, json={"name": "x" * 800_001}).status_code == 413


def test_csrf_and_external_origin_are_rejected(setup):
    _, client, headers, _, project = setup
    assert save(client, {}, project).status_code == 403
    assert save(client, {**headers, "Origin": "https://untrusted.invalid"}, project).status_code == 403
    assert save(client, {**headers, "Origin": "null"}, project).status_code == 403
    assert save(client, headers, project).status_code == 200


def test_stale_save_and_run_do_not_overwrite(setup):
    _, client, headers, _, project = setup
    assert save(client, headers, project).status_code == 200
    assert save(client, headers, project).status_code == 409
    assert run(client, headers, project).status_code == 409


def test_build_work_does_not_change_learn_progress(setup):
    _, client, headers, _, project = setup
    learned = {"computer_os": {"course_complete": True, "completed_lessons": ["hardware"]}}
    with client.session_transaction() as browser:
        browser["learn_progress"] = learned
    assert save(client, headers, project).status_code == 200
    project = client.get(f'/build/projects/{project["id"]}').json["project"]
    assert run(client, headers, project).status_code == 200
    with client.session_transaction() as browser:
        assert browser["learn_progress"] == learned


def test_invalid_run_payload_is_reported_without_server_error(setup):
    _, client, headers, _, project = setup
    assert run(client, headers, project, method=[]).status_code == 400
    assert run(client, headers, project, path="/app.py").status_code == 400
    project["active_file"] = []
    assert save(client, headers, project).status_code == 400


def test_user_html_cannot_break_out_of_initial_json(setup):
    _, client, headers, _, project = setup
    project["name"] = "</script><script>alert('bad')</script>"
    assert save(client, headers, project).status_code == 200
    page = client.get("/build/").get_data(as_text=True)
    assert "<script>alert('bad')</script>" not in page
    assert "\\u003c/script\\u003e" in page


def test_preview_renders_edited_html_css_without_executing_python(setup, monkeypatch):
    _, client, headers, _, project = setup
    project["files"]["templates/index.html"] = '<link rel="stylesheet" href="/static/style.css"><h1>自分の画面</h1>'
    project["files"]["static/style.css"] = "h1 {color: teal}"
    project["files"]["app.py"] = "raise RuntimeError('must not execute on host')"
    project = save(client, headers, project).json["project"]
    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: pytest.fail("No subprocess in HTML mode"))
    result = run(client, headers, project).json
    assert "自分の画面" in result["document"]
    assert "h1 {color: teal}" in result["document"]
    assert "実行していません" in result["logs"]


def test_flask_unavailable_is_explicit_and_never_runs_on_host(setup, monkeypatch):
    _, client, headers, _, project = setup
    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: pytest.fail("Must not start host Python"))
    result = run(client, headers, project, mode="flask")
    assert result.status_code == 400
    assert "未設定" in result.json["error"]


def test_static_forms_do_not_pretend_to_save_data(setup):
    _, client, headers, _, project = setup
    response = run(client, headers, project, method="POST", data={"body": "test"})
    assert response.status_code == 400
    assert "Flaskモードが必要" in response.json["error"]


@pytest.mark.parametrize("path", ["https://example.com/", "//example.com/", "\\\\host\\file", "/%2fexample.com/", "javascript:alert(1)", "/%0dHeader"])
def test_external_preview_paths_are_rejected(path):
    with pytest.raises(ValueError):
        local_path(path)


def test_preview_strips_scripts_external_resources_and_navigation():
    unsafe = '''<base href="https://example.com"><meta http-equiv="refresh" content="0;url=https://example.com">
    <script>alert('bad')</script><svg onload="bad()"></svg><iframe src="/learn/"></iframe>
    <a href="https://example.com">external</a><img src="https://example.com/x" onerror="bad()">
    <form action="/notes" method="post"><input name="body"><button>保存</button></form>
    <p onclick="bad()">safe text</p>'''
    preview = make_preview(unsafe, {})
    document = preview["document"]
    assert document.count("<script") == 1  # 固定のフォーム橋渡しコードだけ。
    assert "alert('bad')" not in document
    for forbidden in ("<iframe", "<svg", "<base", "http-equiv=\"refresh", "onerror", "onclick", "https://example.com"):
        assert forbidden not in document
    assert 'data-build-path="/notes"' in document
    assert "default-src &#x27;none&#x27;" in document
    assert "form-action &#x27;none&#x27;" in document


def test_css_cannot_inject_html():
    document = make_preview('<link rel="stylesheet" href="/static/style.css">', {
        "static/style.css": "</style><script>bad()</script>"
    })["document"]
    assert document.count("<script") == 1
    assert "\\3c /style>" in document


def test_secrets_and_runtime_state_are_not_sent_to_editor(setup):
    _, client, _, owner, project = setup
    private = BuildStore(client.application.instance_path).get(owner, project["id"])
    assert "runtime_secret" not in project
    assert "runtime_state" not in project
    assert private["runtime_secret"] not in client.get("/build/").get_data(as_text=True)
    assert "BUILD_APP_SECRET" in project["files"]["app.py"]
    assert private["runtime_secret"] not in project["files"]["app.py"]


def test_chat_fallback_context_and_history_persist(setup):
    _, client, headers, _, project = setup
    result = client.post(f'/build/projects/{project["id"]}/chat', headers=headers,
                         json={"question": "フォームの入力を受け取りたい", "active_file": "app.py"})
    assert result.status_code == 200
    assert "request.form" in result.json["answer"]
    assert "Learn第4訓練" in result.json["answer"]
    assert "生成AI未接続" in result.json["mode"]
    loaded = client.get(f'/build/projects/{project["id"]}').json["project"]
    assert loaded["chat"] == result.json["chat"]


def test_ai_provider_boundary_and_failure_fallback(setup):
    app, client, headers, _, project = setup

    class TestProvider:
        mode = "テスト用AI"

        def reply(self, context, history, question):
            assert "runtime_secret" not in context
            assert context["active_file"] == "app.py"
            return "Routeを確認しましょう。"

    app.config["BUILD_AI_PROVIDER"] = TestProvider()
    url = f'/build/projects/{project["id"]}/chat'
    data = {"question": "Routeは？", "active_file": "app.py"}
    assert client.post(url, headers=headers, json=data).json["mode"] == "テスト用AI"
    app.config["BUILD_AI_PROVIDER"] = object()
    response = client.post(url, headers=headers, json=data)
    assert response.status_code == 200
    assert "ローカルガイド" in response.json["mode"]


def test_docker_command_has_no_host_mount_or_network():
    command = container_command("cyber-build-test", "unix:///var/run/docker.sock")
    for flag in ("--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                 "--memory=192m", "--memory-swap=192m", "--pids-limit=32", "--user=65534:65534", "--pull=never", "--rm"):
        assert flag in command
    for unsafe in ("--privileged", "-v", "--volume", "--mount", "--env-file", "-p"):
        assert unsafe not in command


def test_runner_result_cannot_write_arbitrary_host_files():
    result = {"html": "<p>OK</p>", "status": 200, "state": {"../../app.py": "bad"}}
    with pytest.raises(ValueError):
        validate_runtime_result(result)
    result["state"] = {"database": base64.b64encode(b"x" * 1_000_001).decode()}
    with pytest.raises(ValueError):
        validate_runtime_result(result)


def test_flask_runtime_boundary_persists_db_and_app_session(setup, monkeypatch):
    app, client, headers, owner, project = setup
    monkeypatch.setattr("src.build_routes.capabilities", lambda: {"available": True})
    encoded = base64.b64encode(b"fake-db-for-boundary-test").decode()

    class TestRuntime:
        def run(self, saved, path, method, data):
            assert saved["files"] == project["files"]
            return {"html": "<p>保存結果</p>", "status": 200, "logs": "POST / -> 200",
                    "state": {"database": encoded, "cookie": "session=project-only"}}

    app.config["BUILD_RUNTIME"] = TestRuntime()
    response = run(client, headers, project, mode="flask", method="POST", data={"body": "abc"})
    assert response.status_code == 200
    loaded = BuildStore(app.instance_path).get(owner, project["id"])
    assert loaded["runtime_state"] == {"database": encoded, "cookie": "session=project-only"}
    with client.session_transaction() as browser:
        assert "project-only" not in str(dict(browser))


def test_runtime_error_keeps_saved_code(setup, monkeypatch):
    app, client, headers, _, project = setup
    monkeypatch.setattr("src.build_routes.capabilities", lambda: {"available": True})

    class FailedRuntime:
        def run(self, *args):
            raise ValueError("実行が10秒を超えました。")

    app.config["BUILD_RUNTIME"] = FailedRuntime()
    assert run(client, headers, project, mode="flask").status_code == 400
    assert client.get(f'/build/projects/{project["id"]}').json["project"] == project


def test_container_is_cleaned_up_after_timeout(monkeypatch):
    from src import build_runtime

    calls = []

    def timed_out(command, payload, **kwargs):
        assert command[0:4] == ["docker", "--host", "unix:///var/run/docker.sock", "start"]
        raise ValueError("実行時間を超えました")

    monkeypatch.setattr(build_runtime, "bounded_container_call", timed_out)
    def command_result(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(build_runtime.subprocess, "run", command_result)
    with pytest.raises(ValueError, match="実行時間"):
        build_runtime.DockerRuntime("unix:///var/run/docker.sock").run({"files": {}, "runtime_state": {}, "runtime_secret": "fixture"}, "/", "GET", {})
    assert calls[0][3] == "create"
    assert calls[1][:5] == ["docker", "--host", "unix:///var/run/docker.sock", "rm", "--force"]
    assert calls[1][5].startswith("cyber-build-")


@pytest.mark.parametrize("endpoint", ["tcp://127.0.0.1:2375", "ssh://remote", "npipe:////remote/pipe/docker", None])
def test_docker_does_not_use_network_daemons(endpoint):
    with pytest.raises(ValueError):
        container_command("cyber-build-test", endpoint)


def test_worker_syntax_error_is_reported_without_losing_state(workspace, monkeypatch):
    from build_runtime import runner

    def invalid_code(*args, **kwargs):
        raise SyntaxError("expected ':' in app.py")

    bundle = {"files": {"app.py": "not executed"}, "secret": "test-only",
              "state": {"cookie": "session=old-state"}, "path": "/", "method": "GET", "data": {}}
    monkeypatch.setattr(runner.runpy, "run_path", invalid_code)
    monkeypatch.setattr(runner.sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(bundle).encode())))
    output = io.StringIO()
    monkeypatch.setattr(runner.sys, "stdout", output)
    monkeypatch.setattr(runner.sys, "path", list(runner.sys.path))
    monkeypatch.setenv("BUILD_APP_SECRET", "before-test")
    runner.main(workspace)
    result = json.loads(output.getvalue())
    assert result["status"] == 500
    assert "SyntaxError" in result["logs"]
    assert result["state"] == bundle["state"]


def test_worker_http_form_session_and_database_with_trusted_fixture(workspace, monkeypatch):
    # 利用者コードは実行しない。runpyを固定のテスト用Flaskアプリに置換する。
    from flask import Flask, request, session
    from build_runtime import runner

    fixture_app = Flask(__name__)
    fixture_app.secret_key = "fixture-only"

    @fixture_app.route("/", methods=["GET", "POST"])
    def index():
        session["seen"] = True
        (workspace / "data" / "app.sqlite3").write_bytes(b"fixture database")
        return "Hello " + request.form.get("body", "world")

    bundle = {"files": {"app.py": "this text is never executed"}, "secret": "test-only",
              "state": {}, "path": "/", "method": "POST", "data": {"body": "Build"}}
    monkeypatch.setattr(runner.runpy, "run_path", lambda *args, **kwargs: {"app": fixture_app})
    monkeypatch.setattr(runner.sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(bundle).encode())))
    output = io.StringIO()
    monkeypatch.setattr(runner.sys, "stdout", output)
    monkeypatch.setattr(runner.sys, "path", list(runner.sys.path))
    monkeypatch.setenv("BUILD_APP_SECRET", "before-test")
    # 本番ランナーはLinux専用。このテストはWindows上で固定アプリの入出力だけを確認する。
    for flag in ("O_NOFOLLOW", "O_NONBLOCK"):
        if not hasattr(runner.os, flag):
            monkeypatch.setattr(runner.os, flag, 0, raising=False)
    runner.main(workspace)
    result = json.loads(output.getvalue())
    assert result["html"] == "Hello Build", result["logs"]
    assert result["status"] == 200
    assert "session=" in result["state"]["cookie"]
    assert base64.b64decode(result["state"]["database"]) == b"fixture database"


def test_preview_navigation_redirect_and_rerun_preserve_project_state(setup, workspace, monkeypatch):
    # 入力コードは実行しない。固定Flaskアプリで実際のRequest・Session・SQLiteを確認する。
    import sqlite3
    from flask import Flask, redirect, request, session
    from build_runtime import runner

    app, client, headers, owner, project = setup
    fixture_app = Flask(__name__)
    fixture_app.secret_key = "fixture-only"

    @fixture_app.get("/")
    def home():
        with sqlite3.connect(workspace / "data" / "app.sqlite3") as db:
            db.execute("CREATE TABLE IF NOT EXISTS notes (body TEXT)")
            rows = db.execute("SELECT body FROM notes").fetchall()
        return f'<p>session={session.get("count", 0)}; rows={rows}</p><a href="/detail">Detail</a>'

    @fixture_app.get("/detail")
    def detail():
        return '<form action="/save" method="post"><input name="body"><button>Save</button></form>'

    @fixture_app.post("/save")
    def submit():
        session["count"] = session.get("count", 0) + 1
        with sqlite3.connect(workspace / "data" / "app.sqlite3") as db:
            db.execute("INSERT INTO notes VALUES (?)", (request.form["body"],))
        return redirect("/")

    monkeypatch.setattr("src.build_routes.capabilities", lambda: {"available": True})
    monkeypatch.setattr(runner.runpy, "run_path", lambda *args, **kwargs: {"app": fixture_app})
    for flag in ("O_NOFOLLOW", "O_NONBLOCK"):
        if not hasattr(runner.os, flag):
            monkeypatch.setattr(runner.os, flag, 0, raising=False)

    class TrustedRuntime:
        def run(self, saved, path, method, data):
            bundle = {"files": saved["files"], "secret": saved["runtime_secret"],
                      "state": saved["runtime_state"], "path": path, "method": method, "data": data}
            output = io.StringIO()
            with monkeypatch.context() as worker:
                worker.setattr(runner.sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(bundle).encode())))
                worker.setattr(runner.sys, "stdout", output)
                worker.setattr(runner.sys, "path", list(runner.sys.path))
                worker.setenv("BUILD_APP_SECRET", "fixture-only")
                runner.main(workspace)
            return json.loads(output.getvalue())

    app.config["BUILD_RUNTIME"] = TrustedRuntime()
    assert run(client, headers, project, mode="flask").json["status"] == 200
    detail_response = run(client, headers, project, mode="flask", path="/detail").json
    assert 'data-build-path="/save"' in detail_response["document"]
    response = run(client, headers, project, mode="flask", path="/save", method="POST", data={"body": "kept"}).json
    assert response["status"] == 200
    assert "POST /save -> 302" in response["logs"]
    assert "GET / -> 200" in response["logs"]
    assert "session=1" in response["document"] and "kept" in response["document"]

    store = BuildStore(app.instance_path)
    before = store.get(owner, project["id"])
    client.post(f'/build/projects/{project["id"]}/chat', headers=headers,
                json={"question": "Route", "active_file": "app.py"})
    # コード保存を挟んでも、RUNは同じプロジェクトのSession・DBを使う。
    project["files"]["app.py"] = "replacement code (never executed in this test)"
    project = save(client, headers, project).json["project"]
    response = run(client, headers, project, mode="flask", path="/", method="GET").json
    assert response["status"] == 200
    assert "session=1" in response["document"] and "kept" in response["document"]
    after = store.get(owner, project["id"])
    assert after["runtime_state"] == before["runtime_state"]
    assert after["runtime_secret"] == before["runtime_secret"]
    assert client.get(f'/build/projects/{project["id"]}').json["project"] == project
    assert len(project["chat"]) == 2
