"""Phase 3の状態・コピー・安全境界。利用者コードをホストで実行しない。"""

import ast
import copy
import json
import os
import random
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from src.app import create_app
from src.arena_engine import (begin_attack, fill_targets, pulse_due, snapshot_defend,
                              public_state, request_values, validate_policy)
from src.arena_scenarios import SCENARIOS, DEFEND_SCENARIOS, DIFFICULTIES
from src.arena_store import ArenaStore
from src.arena_targets import target_files
from src.build_runtime import DockerRuntime, container_command, runtime_status
from src.build_store import BuildStore
from test_build import workspace


class FixedRuntime:
    """進行テスト専用。保存したコードは解析・実行しない。"""
    def __init__(self):
        self.calls = []
        self.marker = ""
        self.status = 200

    def run(self, project, path, method, data):
        self.calls.append((copy.deepcopy(project), path, method, data))
        return {"html": self.marker if data.get("solve") == "yes" else '<script>alert(1)</script>response',
                "status": self.status, "state": {"cookie": "training=copy-only", "database": ""},
                "logs": f"{method} {path} -> {self.status}"}


@pytest.fixture
def arena_setup(workspace, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("src.arena_routes.runtime_status", lambda enabled: {"available": True})
    app = create_app(workspace)
    app.config.update(TESTING=True, ARENA_RUNTIME=FixedRuntime(), ARENA_RANDOM=random.Random(7), ARENA_HARD_DELAY=(10, 10))
    client = app.test_client()
    page = client.get("/arena/")
    initial = json.loads(re.search(r'<script id="arena-initial" type="application/json">(.*?)</script>', page.text, re.S)[1])
    with client.session_transaction() as cookie:
        owner = cookie["build_owner"]
    return app, client, {"X-Build-CSRF": initial["csrf"]}, owner, initial["state"]


def act(setup, action, **fields):
    _, client, headers, _, _ = setup
    return client.post("/arena/action", headers=headers, json={"action": action, **fields})


def state(setup):
    app, _, _, owner, _ = setup
    with ArenaStore(app.instance_path).edit(owner) as saved:
        return copy.deepcopy(saved)


def select(setup):
    target = state(setup)["targets"][0]
    return act(setup, "attack-select", target=target["id"]).json["state"]["attack"]


def send(setup, attack, **fields):
    return act(setup, "attack-request", attempt=attack["id"], sequence=attack["count"], path="/", **fields)


def make_copy(setup, scenario="repeated-reads"):
    app, _, _, owner, _ = setup
    project = BuildStore(app.instance_path).create(owner, "Defend fixture")
    result = act(setup, "defend-copy", project=project["id"], scenario=scenario, path="/")
    return project, result.json["state"]["defend"]


def test_home_defaults_targets_no_spoilers(arena_setup):
    _, client, _, _, initial = arena_setup
    assert initial["difficulty"] == "easy"
    assert len(initial["targets"]) == 3
    assert len({target["title"] for target in initial["targets"]}) == 3
    assert "marker" not in str(initial) and "vulnerability" not in str(initial)
    page = client.get("/arena/").text
    assert "ATTACK" in page and "DEFEND" in page and "HARD" in page
    assert 'class="hud-interface ' in page
    assert client.get("/learn/").status_code == 200
    assert client.get("/build/").status_code == 200  # 所有者CookieをBuildと互換に保つ。


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_difficulty_hint_boundary(arena_setup, difficulty):
    assert act(arena_setup, "difficulty", value=difficulty).status_code == 200
    select(arena_setup)
    reply = act(arena_setup, "hint", mode="attack")
    if difficulty == "easy":
        assert len(reply.json["state"]["attack"]["hints"]) == 1
        assert len(act(arena_setup, "hint", mode="attack").json["state"]["attack"]["hints"]) == 2
    else:
        assert reply.status_code == 400
        assert public_state(state(arena_setup))["attack"]["hints"] == []


def test_attack_success_replaces_only_one_and_no_duplicate(arena_setup):
    app, _, _, _, _ = arena_setup
    before = state(arena_setup)["targets"]
    attack = select(arena_setup)
    app.config["ARENA_RUNTIME"].marker = state(arena_setup)["attack"]["marker"]
    reply = send(arena_setup, attack, fields={"solve": "yes"})
    result = reply.json["state"]
    assert result["attack"]["status"] == "success"
    after = state(arena_setup)["targets"]
    assert before[1:] == after[1:]
    assert before[0]["scenario"] != after[0]["scenario"]
    assert len({item["scenario"] for item in after}) == 3
    assert result["attack"]["advice"] and result["history"][-1]["passed"]
    assert send(arena_setup, attack, fields={"solve": "yes"}).status_code == 400
    assert len(state(arena_setup)["history"]) == 1


def test_attack_failed_limit_and_stale_post(arena_setup):
    attack = select(arena_setup)
    original = copy.deepcopy(attack)
    for _ in range(attack["limit"]):
        attack = send(arena_setup, attack, fields={}).json["state"]["attack"]
    assert attack["status"] == "failed" and attack["advice"]
    assert send(arena_setup, original, fields={}).status_code == 400
    assert len(state(arena_setup)["targets"]) == 3


def test_attack_manual_end_and_duplicate_sequence(arena_setup):
    attack = select(arena_setup)
    assert send(arena_setup, attack, fields={}).status_code == 200
    assert send(arena_setup, attack, fields={}).status_code == 400
    result = act(arena_setup, "attack-finish", attempt=attack["id"]).json["state"]
    assert result["attack"]["status"] == "failed"
    assert act(arena_setup, "attack-finish", attempt=attack["id"]).status_code == 400


@pytest.mark.parametrize("path", ["https://example.invalid", "//192.0.2.1/", "/%2fexample.invalid/", "/\\host", "/\nGET", "C:\\secret"])
def test_external_paths_rejected(arena_setup, path):
    attack = select(arena_setup)
    response = act(arena_setup, "attack-request", attempt=attack["id"], sequence=0, path=path, fields={})
    assert response.status_code == 400
    assert not arena_setup[0].config["ARENA_RUNTIME"].calls


@pytest.mark.parametrize("scenario", list(DEFEND_SCENARIOS))
def test_defend_copy_success_and_original_unchanged(arena_setup, scenario):
    app, _, _, owner, _ = arena_setup
    project, defend = make_copy(arena_setup, scenario)
    database = BuildStore(app.instance_path)
    before = database.get(owner, project["id"])
    started = act(arena_setup, "defend-start", attempt=defend["id"]).json["state"]["defend"]
    assert started["status"] == "incident"
    assert "probe-" in "\n".join(started["logs"])
    assert state(arena_setup)["defend"]["project"]["runtime_state"] != before["runtime_state"]
    policy = {"blocked_sources": ["probe-" + defend["id"][:4]], "max_body": 10000}
    if scenario == "oversized-input":
        policy = {"blocked_sources": [], "max_body": 500}
    reply = act(arena_setup, "defend-assess", attempt=defend["id"], policy=policy)
    assert reply.json["state"]["defend"]["status"] == "success"
    assert database.get(owner, project["id"]) == before
    assert act(arena_setup, "defend-assess", attempt=defend["id"], policy=policy).status_code == 400


@pytest.mark.parametrize("block_visitor", [False, True])
def test_defend_failure_feedback_and_availability(arena_setup, block_visitor):
    _, defend = make_copy(arena_setup)
    act(arena_setup, "defend-start", attempt=defend["id"])
    sources = ["visitor", "probe-" + defend["id"][:4]] if block_visitor else []
    result = act(arena_setup, "defend-assess", attempt=defend["id"],
                 policy={"blocked_sources": sources, "max_body": 10000}).json["state"]["defend"]
    assert result["status"] == "failed"
    assert "Build" in result["advice"] and result["related_learn"]


def test_hard_timer_automatic_no_manual_start_and_single_event(arena_setup):
    app, _, _, owner, _ = arena_setup
    BuildStore(app.instance_path).create(owner, "Hard copy")
    app.config["ARENA_HARD_DELAY"] = (0, 0)
    result = act(arena_setup, "difficulty", value="hard").json["state"]
    assert result["defend"]["status"] == "armed"
    assert act(arena_setup, "defend-start", attempt=result["defend"]["id"]).status_code == 400
    updated = act(arena_setup, "pulse", view=result["view"]).json["state"]
    assert updated["defend"]["status"] == "incident"
    calls = len(app.config["ARENA_RUNTIME"].calls)
    act(arena_setup, "pulse", view=result["view"])
    assert len(app.config["ARENA_RUNTIME"].calls) == calls
    logs = "\n".join(updated["defend"]["logs"])
    assert "-b" in logs


def test_hard_presence_inactive_pause_and_tab_lease(arena_setup):
    _, defend = make_copy(arena_setup)
    saved = state(arena_setup)
    saved["difficulty"] = "hard"
    saved["defend"].update(status="armed", remaining=10, last_pulse=None)
    assert not pulse_due(saved, saved["view"], 10)
    assert not pulse_due(saved, saved["view"], 13)
    assert saved["defend"]["remaining"] == 7
    assert not pulse_due(saved, "other-tab", 16)
    assert not pulse_due(saved, saved["view"], 1000)  # 不在時間を一括加算しない。
    assert saved["defend"]["remaining"] == 7
    pulse_due(saved, saved["view"], 1001, paused=True)
    pulse_due(saved, saved["view"], 1002)
    assert saved["defend"]["remaining"] == 7


def test_restart_persistence_and_owner_isolation(arena_setup, workspace):
    app, client, headers, owner, _ = arena_setup
    attack = select(arena_setup)
    second = create_app(workspace).test_client()
    second.set_cookie("session", client.get_cookie("session").value)
    assert second.get("/arena/").status_code == 200
    assert state(arena_setup)["attack"]["id"] == attack["id"]
    stranger = app.test_client()
    stranger.get("/arena/")
    with stranger.session_transaction() as cookie:
        foreign_headers = {"X-Build-CSRF": cookie["build_csrf"]}
    project = BuildStore(workspace).create(owner, "private")
    assert stranger.post("/arena/action", headers=foreign_headers,
                         json={"action": "defend-copy", "project": project["id"], "scenario": "repeated-reads"}).status_code == 404
    assert client.post("/arena/action", json={"action": "difficulty", "value": "hard"}).status_code == 403
    assert client.post("/arena/action", headers={**headers, "Origin": "https://untrusted.invalid"},
                       json={"action": "difficulty", "value": "hard"}).status_code == 403


def test_runtime_unavailable_does_not_advance(arena_setup, monkeypatch):
    app, _, _, _, _ = arena_setup
    app.config.pop("ARENA_RUNTIME")
    monkeypatch.setattr("src.arena_routes.runtime_status", lambda enabled: {"available": False})
    attack = select(arena_setup)
    assert send(arena_setup, attack, fields={}).status_code == 400
    assert state(arena_setup)["attack"]["count"] == 0


def test_sandbox_command_has_no_host_mounts_or_network():
    command = container_command("test", "unix:///var/run/docker.sock")
    for flag in ("--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user=65534:65534", "--pull=never"):
        assert flag in command
    assert not any(arg in ("--volume", "-v", "--mount", "-p", "--publish", "--privileged", "--env") for arg in command)
    assert not any(".git" in arg or "OPENAI" in arg for arg in command)


@pytest.mark.parametrize("scenario_id", list(SCENARIOS))
def test_scenario_definition_and_target_syntax(scenario_id):
    scenario = SCENARIOS[scenario_id]
    assert scenario["success_condition"] == "response_marker"
    assert scenario["easy_hints"] and scenario["post_failure_advice"] and scenario["related_learn"]
    ast.parse(target_files(scenario, "LAB-fixture")["app.py"])  # 構文確認のみ。実行しない。


@pytest.mark.parametrize("scenario_id", list(SCENARIOS))
@pytest.mark.skipif(os.environ.get("ARENA_DOCKER_TESTS") != "1", reason="Explicit local Docker integration run only")
def test_actual_docker_targets(scenario_id):
    status = runtime_status(True)
    assert status["available"], status
    runtime = DockerRuntime(status["endpoint"])
    scenario = SCENARIOS[scenario_id]
    project = {"files": target_files(scenario, "LAB-integration"), "runtime_state": {}, "runtime_secret": "isolated-test-key"}
    def request(path, method="GET", data=None):
        result = runtime.run(project, path, method, data or {})
        project["runtime_state"] = result["state"]
        return result
    assert request("/")["status"] == 200
    if scenario["difficulty"] == "hard":
        assert request("/catalog")["status"] == 403
        assert request("/connect", "POST", {"team": "guest"})["status"] == 200
        assert request("/catalog")["status"] == 200
    requests = {"records": ("/records", "GET", {"id": "7317" if scenario["difficulty"] == "hard" else "102"}),
                "exports": ("/export", "POST", {"scope": "internal"}),
                "search": ("/search", "GET", {"q": "' OR 1=1 --"}),
                "support": ("/support", "GET", {"view": "full"})}
    result = request(*requests[scenario["family"]])
    assert result["status"] == 200 and "LAB-integration" in result["html"], result


def test_arena_javascript_events():
    result = subprocess.run([shutil.which("node"), str(Path(__file__).with_name("arena_checks.cjs"))],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
