"""演習の進行。HTTPはDocker内のFlaskへ送り、ネットワーククライアントは持たない。"""

import copy
import secrets
from urllib.parse import urlsplit

from src.arena_scenarios import SCENARIOS, DEFEND_SCENARIOS
from src.arena_targets import target_files
from src.build_ai_context import redact, secret_values
from src.build_preview import local_path
from src.build_runtime import validate_runtime_result


def candidates(difficulty):
    return [key for key, item in SCENARIOS.items() if item["difficulty"] == difficulty]


def fill_targets(state, rng, replace=None):
    existing = [target["scenario"] for target in state["targets"] if target["id"] != replace]
    old = next((target["scenario"] for target in state["targets"] if target["id"] == replace), None)
    choices = [key for key in candidates(state["difficulty"]) if key not in existing and key != old]
    if replace:
        target = next(target for target in state["targets"] if target["id"] == replace)
        target.update(id=secrets.token_hex(12), scenario=rng.choice(choices))
    else:
        state["targets"] = [{"id": secrets.token_hex(12), "scenario": key}
                            for key in rng.sample(candidates(state["difficulty"]), 3)]


def begin_attack(state, target_id):
    if state["attack"] and state["attack"]["status"] == "active":
        raise ValueError("現在の挑戦を終了してから選択してください。")
    target = next((item for item in state["targets"] if item["id"] == target_id), None)
    if target is None:
        raise ValueError("対象を選び直してください。")
    scenario = SCENARIOS[target["scenario"]]
    marker = "LAB-" + secrets.token_hex(12)
    state["attack"] = {"id": secrets.token_hex(12), "target_id": target_id, "scenario": scenario["id"],
        "status": "active", "count": 0, "hint": 0, "logs": [], "response": "まず GET / を送信してください。",
        "http_status": None, "marker": marker,
        "project": {"files": target_files(scenario, marker), "runtime_state": copy.deepcopy(scenario["initial_state"]),
                    "runtime_secret": secrets.token_hex(32)}}


def request_values(data):
    path = data.get("path", "/")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError("仮想ターゲット内の / から始まるパスを指定してください。")
    path = local_path(path)
    method = data.get("method", "GET")
    fields = data.get("fields", {})
    if method not in ("GET", "POST"):
        raise ValueError("GET / POSTだけを指定できます。")
    if not isinstance(fields, dict) or len(fields) > 20:
        raise ValueError("入力は20項目以内のJSONオブジェクトにしてください。")
    if any(not isinstance(key, str) or len(key) > 80 or not isinstance(value, str) or len(value) > 5000
           for key, value in fields.items()) or sum(len(value) for value in fields.values()) > 12000:
        raise ValueError("入力項目の種類・長さを確認してください。")
    return path, method, fields


def execute(runtime, project, path, method, data):
    result = validate_runtime_result(runtime.run(project, path, method, data))
    project["runtime_state"] = result["state"]
    hidden = secret_values(project)
    return {"http_status": result["status"], "response": redact(result["html"], hidden)[:16000],
            "logs": redact(result["logs"], hidden)[-3000:]}


def record_result(state, mode, title, passed):
    state["history"] = (state["history"] + [{"mode": mode, "title": title,
        "difficulty": state["difficulty"], "passed": passed}])[-10:]


def finish_attack(state, passed, rng):
    attack = state["attack"]
    if not attack or attack["status"] != "active":
        raise ValueError("この挑戦は終了しています。")
    attack["status"] = "success" if passed else "failed"
    record_result(state, "ATTACK", SCENARIOS[attack["scenario"]]["title"], passed)
    fill_targets(state, rng, attack["target_id"])


def attack_request(state, data, runtime, rng):
    attack = state["attack"]
    if not attack or attack["status"] != "active" or data.get("attempt") != attack["id"]:
        raise ValueError("現在の挑戦を確認してください。")
    # UIの二重送信や遅延した要求を同じ問題番号で受理しない。
    if type(data.get("sequence")) is not int or data["sequence"] != attack["count"]:
        raise ValueError("直前の応答を確認してから送信してください。")
    path, method, fields = request_values(data)
    result = execute(runtime, attack["project"], path, method, fields)
    attack["count"] += 1
    attack.update(response=result["response"], http_status=result["http_status"])
    attack["logs"] = (attack["logs"] + [f'{method} {path} -> {result["http_status"]}\n{result["logs"]}'])[-14:]
    passed = result["http_status"] == 200 and attack["marker"] in result["response"]
    if passed or attack["count"] >= SCENARIOS[attack["scenario"]]["request_limit"]:
        finish_attack(state, passed, rng)


def snapshot_defend(state, project, scenario_id, path, rng, delay):
    if not isinstance(scenario_id, str) or scenario_id not in DEFEND_SCENARIOS:
        raise ValueError("防御シナリオを選んでください。")
    path, _, _ = request_values({"path": path})
    if urlsplit(path).query:
        raise ValueError("防御対象はクエリなしのパスを指定してください。")
    if "app.py" not in project["files"]:
        raise ValueError("Flaskのapp.pyがあるBuildプロジェクトを選んでください。")
    state["defend"] = {"id": secrets.token_hex(12), "source_id": project["id"], "source_name": project["name"],
        "source_revision": project["revision"], "scenario": scenario_id, "path": path,
        "status": "armed" if state["difficulty"] == "hard" else "ready", "hint": 0, "logs": [],
        "response": "コピーを作成しました。元のBuildプロジェクトへ書き戻すことはありません。",
        "project": copy.deepcopy({key: project[key] for key in ("files", "runtime_state", "runtime_secret")}),
        "remaining": rng.uniform(*delay), "last_pulse": None, "policy": {"blocked_sources": [], "max_body": 10000}}


def defend_events(defend, difficulty):
    scenario = DEFEND_SCENARIOS[defend["scenario"]]
    suffix = defend["id"][:4]
    probes = [f"probe-{suffix}", f"probe-{suffix}-b" if difficulty == "hard" else f"probe-{suffix}"]
    return [
        {"source": "visitor", "method": "GET", "data": {}, "attack": False},
        {"source": probes[0], "method": scenario["method"], "data": scenario["data"], "attack": True},
        {"source": probes[1], "method": scenario["method"], "data": scenario["data"], "attack": True},
        {"source": "visitor", "method": "GET", "data": {}, "attack": False},
    ]


def validate_policy(policy):
    if not isinstance(policy, dict) or set(policy) != {"blocked_sources", "max_body"}:
        raise ValueError("blocked_sourcesとmax_bodyを含むJSONを入力してください。")
    sources = policy["blocked_sources"]
    if not isinstance(sources, list) or len(sources) > 10 or any(
            not isinstance(item, str) or len(item) > 40 for item in sources):
        raise ValueError("blocked_sourcesは送信元ラベルの配列（10件まで）です。")
    if type(policy["max_body"]) is not int or not 0 <= policy["max_body"] <= 10000:
        raise ValueError("max_bodyは0〜10000の整数です。")
    return policy


def run_defend_events(defend, difficulty, runtime, policy):
    outcomes = []
    for event in defend_events(defend, difficulty):
        size = sum(len(value.encode("utf-8")) for value in event["data"].values())
        blocked = event["source"] in policy["blocked_sources"] or size > policy["max_body"]
        result = {"http_status": 403 if event["source"] in policy["blocked_sources"] else 413,
                  "response": "演習用の入口制御で拒否しました。", "logs": ""}
        if not blocked:
            result = execute(runtime, defend["project"], defend["path"], event["method"], event["data"])
        defend["logs"].append(f'{event["source"]} | {event["method"]} {defend["path"]} | bytes={size} | '
                              f'{result["http_status"]} | {"GATE BLOCK" if blocked else "APP"}\n{result["logs"]}')
        defend["response"] = result["response"]
        if event["attack"]:
            outcomes.append(blocked or result["http_status"] in (400, 401, 403, 405, 413, 422, 429))
        else:
            outcomes.append(200 <= result["http_status"] < 400)
    defend["logs"] = defend["logs"][-12:]
    return all(outcomes)


def start_defend(state, runtime):
    defend = state["defend"]
    if not defend or defend["status"] not in ("ready", "armed"):
        raise ValueError("待機中の隔離コピーを選んでください。")
    # 対象の通常画面が動かない場合、演習失敗とはせずBuildで修正してもらう。
    baseline = execute(runtime, defend["project"], defend["path"], "GET", {})
    if not 200 <= baseline["http_status"] < 400:
        raise ValueError("コピーの通常GETが成功しません。Buildで実行と対象パスを確認してください。")
    run_defend_events(defend, state["difficulty"], runtime, defend["policy"])
    defend["status"] = "incident"
    defend["last_pulse"] = None


def assess_defend(state, data, runtime):
    defend = state["defend"]
    if not defend or defend["status"] != "incident" or data.get("attempt") != defend["id"]:
        raise ValueError("発生中の演習を確認してください。")
    policy = validate_policy(data.get("policy"))
    passed = run_defend_events(defend, state["difficulty"], runtime, policy)
    defend.update(policy=policy, status="success" if passed else "failed")
    record_result(state, "DEFEND", DEFEND_SCENARIOS[defend["scenario"]]["title"], passed)


def pulse_due(state, view, now, paused=False):
    defend = state["defend"]
    if view != state["view"] or state["difficulty"] != "hard" or not defend or defend["status"] != "armed":
        return False
    previous = defend["last_pulse"]
    defend["last_pulse"] = None if paused else now
    if paused:
        return False
    # 非表示・閉じた時間・通信途絶はカウントしない。最新のタブだけが進められる。
    if previous is not None and 0 <= now - previous <= 8:
        defend["remaining"] -= min(now - previous, 3.5)
    return defend["remaining"] <= 0


def public_state(state):
    result = {"difficulty": state["difficulty"], "history": state["history"], "view": state["view"],
              "targets": [], "attack": None, "defend": None}
    for target in state["targets"]:
        scenario = SCENARIOS[target["scenario"]]
        result["targets"].append({"id": target["id"], **{key: scenario[key] for key in
                                  ("title", "target_type", "description", "difficulty")}})
    for mode, definitions in (("attack", SCENARIOS), ("defend", DEFEND_SCENARIOS)):
        attempt = state[mode]
        if not attempt:
            continue
        scenario = definitions[attempt["scenario"]]
        visible = {key: attempt[key] for key in ("id", "status", "logs", "response")}
        visible.update(title=scenario["title"], hints=[], related_learn=[])
        ended = attempt["status"] in ("success", "failed")
        if state["difficulty"] == "easy":
            visible["hints"] = scenario["easy_hints"][:attempt["hint"]]
            visible["related_learn"] = scenario["related_learn"]
        if ended:
            visible.update(advice=scenario.get("post_failure_advice", scenario.get("advice")),
                           related_learn=scenario["related_learn"])
        if mode == "attack":
            visible.update(objective=scenario["objective"], count=attempt["count"],
                           limit=scenario["request_limit"], http_status=attempt["http_status"])
            if ended:
                visible["cause"] = scenario["vulnerability"]
        else:
            visible.update(description=scenario["description"], path=attempt["path"], policy=attempt["policy"],
                           source_id=attempt["source_id"], source_name=attempt["source_name"],
                           source_revision=attempt["source_revision"])
        result[mode] = visible
    return result
