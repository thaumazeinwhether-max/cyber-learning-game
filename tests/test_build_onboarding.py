"""初回案内の永続化・既存データ保護。外部APIは呼ばない。"""

import json
import shutil
import subprocess
from pathlib import Path

import httpx
import pytest

from src.app import create_app
from src.build_onboarding import PLAN_KEYS
from src.build_openai import OpenAIGuide
from src.build_store import BuildStore
from test_build import setup, workspace
from test_build_ai import completed, mock_sdk


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request",
                        lambda *args: pytest.fail("No live HTTP in onboarding tests"))


def propose(client, headers, idea="自分が見た映画を記録するアプリを作りたい"):
    return client.post("/build/onboarding/plan", headers=headers, json={"idea": idea})


def finish(client, headers, **data):
    return client.post("/build/onboarding/complete", headers=headers, json=data)


def test_first_visit_local_plan_and_no_project_mutation(setup):
    app, client, headers, owner, project = setup
    database = BuildStore(app.instance_path)
    before = database.get(owner, project["id"])
    assert 'id="onboarding-dialog"' in client.get("/build/").text
    result = propose(client, headers).json
    assert result["status"] == "local"
    assert set(result["plan"]) == set(PLAN_KEYS)
    assert "映画" in result["plan"]["purpose"]
    assert "SQLite" in result["plan"]["learn"]
    assert "templates/index.html" in result["plan"]["first_step"]
    assert "ログイン" not in result["plan"]["features"]
    assert database.onboarding(owner)["required"]
    assert before == database.get(owner, project["id"])


@pytest.mark.parametrize("idea", ["", "  ", "a" * 1501, None, [], 42])
def test_invalid_free_input(setup, idea):
    _, client, headers, _, _ = setup
    assert propose(client, headers, idea).status_code == 400


def test_unknown_idea_and_maximum_input_remain_free(setup):
    _, client, headers, _, _ = setup
    idea = "星座を眺める自分だけのページ".ljust(1500, "あ")
    assert len(idea) == 1500
    plan = propose(client, headers, idea).json["plan"]
    assert plan["purpose"] == idea
    assert "第6訓練" in plan["learn"] and "SQLite" not in plan["learn"]


@pytest.mark.parametrize("action", ["start", "skip"])
def test_finish_skip_restart_and_other_projects(setup, workspace, action):
    app, client, headers, owner, project = setup
    plan = propose(client, headers).json["plan"]
    plan["features"] = "自分で選んだ候補だけ"  # 提案の修正・削除が保存される。
    plan["learn"] = ""
    before = BuildStore(workspace).get(owner, project["id"])
    response = finish(client, headers, action=action, plan=plan)
    assert response.status_code == 200
    assert response.json["onboarding"] == {"required": False, "plan": plan if action == "start" else {}}
    assert before == BuildStore(workspace).get(owner, project["id"])
    assert 'id="onboarding-dialog"' not in client.get("/build/").text
    other = client.post("/build/projects", headers=headers, json={"name": "自由な別プロジェクト"})
    assert other.status_code == 201
    assert 'id="onboarding-dialog"' not in client.get("/build/").text
    restarted = create_app(workspace).test_client()
    restarted.set_cookie("session", client.get_cookie("session").value)
    assert 'id="onboarding-dialog"' not in restarted.get("/build/").text
    # 遅延した別タブのスキップも確認済みの内容を消さない。
    finish(client, headers, action="skip")
    assert BuildStore(workspace).onboarding(owner) == response.json["onboarding"]


def test_unfinished_guide_survives_restart(setup, workspace):
    _, client, _, _, _ = setup
    restarted = create_app(workspace).test_client()
    restarted.set_cookie("session", client.get_cookie("session").value)
    assert 'id="onboarding-dialog"' in restarted.get("/build/").text


def test_legacy_database_migration_preserves_every_project_field(workspace, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    database = BuildStore(workspace)
    first = database.create("old-owner", "既存プロジェクト")
    second = database.create("old-owner", "別プロジェクト")
    database.save_runtime("old-owner", first["id"], 1, {"database": "opaque DB bytes", "cookie": "session=keep"})
    database.save_chat("old-owner", first["id"], [{"role": "user", "text": "既存の相談"}])
    before = [database.get("old-owner", p["id"]) for p in (first, second)]
    with database.connect() as db:
        db.execute("DROP TABLE build_onboarding")  # 旧版と同じschemaをテスト用DBだけに再現する。
    client = create_app(workspace).test_client()
    with client.session_transaction() as session:
        session["build_owner"] = "old-owner"
        session["build_csrf"] = "test-csrf"
        session["build_project"] = first["id"]
    assert 'id="onboarding-dialog"' not in client.get("/build/").text
    database = BuildStore(workspace)
    assert database.onboarding("old-owner") == {"required": False, "plan": {}}
    assert before == [database.get("old-owner", p["id"]) for p in (first, second)]


def test_provider_uses_existing_sdk_and_minimal_masked_context(setup, monkeypatch):
    app, client, headers, owner, project = setup
    local = propose(client, headers).json["plan"]
    requests, options = mock_sdk(monkeypatch, lambda _: httpx.Response(200, json=completed(json.dumps(local))))
    app.config["BUILD_AI_PROVIDER"] = OpenAIGuide("fixture-key")
    secret = BuildStore(app.instance_path).get(owner, project["id"])["runtime_secret"]
    response = propose(client, headers, "作りたいもの " + secret)
    assert response.json["status"] == "generated"
    assert response.json["plan"] == local
    body = json.loads(requests[0].content)
    data = json.loads(body["input"][0]["content"])
    assert data["context"]["task"] == "onboarding"
    assert set(data["context"]) == {"task", "project_name", "files", "learn_topics"}
    assert data["history"] == [] and secret not in str(data)
    assert "[REDACTED]" in data["question"]
    assert options[0]["timeout"] == 30 and options[0]["max_retries"] == 0
    assert "onboarding" in body["instructions"]


@pytest.mark.parametrize("answer", [None, "not JSON", '{"purpose": 1}', json.dumps(dict.fromkeys(PLAN_KEYS, "x" * 1501))])
def test_provider_failure_or_invalid_output_falls_back(setup, answer):
    app, client, headers, _, _ = setup
    class Provider:
        mode = "test provider"
        def reply(self, context, history, question):
            if answer is None:
                raise RuntimeError("private error details")
            return answer
    app.config["BUILD_AI_PROVIDER"] = Provider()
    result = propose(client, headers).json
    assert result["status"] == "fallback"
    assert "ローカルガイド" in result["mode"]
    assert "private error" not in str(result)
    assert "映画" in result["plan"]["purpose"]


def test_escaped_saved_proposal_and_secrets(setup):
    _, client, headers, _, _ = setup
    attack = '</script><script>alert("x")</script><img src=x onerror=alert(1)>'
    result = propose(client, headers, attack + '\npassword="hide-this-value"').json
    assert "hide-this-value" not in str(result)
    assert attack in result["plan"]["purpose"]
    assert finish(client, headers, action="start", plan=result["plan"]).status_code == 200
    page = client.get("/build/").text
    assert attack not in page and "\\u003cscript\\u003e" in page


@pytest.mark.parametrize("data", [{}, {"action": []}, {"action": "start", "plan": []},
                                  {"action": "start", "plan": dict.fromkeys(PLAN_KEYS, "x" * 1501)}])
def test_invalid_completion_does_not_finish(setup, data):
    app, client, headers, owner, _ = setup
    assert finish(client, headers, **data).status_code == 400
    assert BuildStore(app.instance_path).onboarding(owner)["required"]


def test_owner_isolation_csrf_and_normal_chat(setup):
    app, client, headers, owner, project = setup
    assert propose(client, {}).status_code == 403
    assert finish(client, {}, action="skip").status_code == 403
    stranger = app.test_client()
    stranger.get("/build/")
    finish(client, headers, action="skip")
    assert 'id="onboarding-dialog"' in stranger.get("/build/").text
    reply = client.post(f'/build/projects/{project["id"]}/chat', headers=headers,
                        json={"question": "フォームを作るには？", "active_file": project["active_file"]})
    assert reply.status_code == 200 and len(reply.json["chat"]) == 2
    assert "request.form" in reply.json["answer"]
    assert client.get("/learn/").status_code == 200


@pytest.mark.parametrize("scenario", ["flow", "skip_pending", "failure", "completed", "save_failure", "revise"])
def test_onboarding_browser_events(scenario):
    result = subprocess.run([shutil.which("node"), str(Path(__file__).with_name("build_onboarding_checks.cjs")), scenario],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
