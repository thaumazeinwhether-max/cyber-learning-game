"""Phase 3の画面・操作境界。ユーザーコードを本体では実行しない。"""

import random
import secrets
import sqlite3
import time

from flask import Blueprint, current_app, jsonify, render_template, request, session

from src.arena_engine import (fill_targets, begin_attack, attack_request, finish_attack, snapshot_defend,
                              start_defend, assess_defend, pulse_due, public_state)
from src.arena_scenarios import DIFFICULTIES, DEFEND_SCENARIOS
from src.arena_store import ArenaStore
from src.build_routes import protect_build, build_headers, run_lock
from src.build_store import BuildStore
from src.build_runtime import DockerRuntime, runtime_status

arena = Blueprint("arena", __name__, url_prefix="/arena")
arena.before_request(protect_build)
arena.after_request(build_headers)


@arena.errorhandler(ValueError)
def invalid(error):
    return jsonify(error=str(error)), 400


@arena.errorhandler(LookupError)
def missing(error):
    return jsonify(error="対象のプロジェクトが見つかりません。"), 404


@arena.errorhandler(sqlite3.OperationalError)
def occupied(error):
    return jsonify(error="別の操作を処理中です。少し待って再読み込みしてください。"), 409


def store():
    return ArenaStore(current_app.instance_path)


def rng():
    return current_app.config.get("ARENA_RANDOM", random)


def delay():
    return current_app.config.get("ARENA_HARD_DELAY", (20, 45))


def runtime():
    # 固定の偽ランナーを使えるのはテスト時だけ。本番では必ず既存Docker境界を通す。
    if current_app.testing and current_app.config.get("ARENA_RUNTIME"):
        return current_app.config["ARENA_RUNTIME"]
    status = runtime_status(current_app.config["BUILD_DOCKER_ENABLED"])
    if not status["available"]:
        raise ValueError("演習にはBuildと同じローカルDocker実行環境が必要です。実行環境を確認してください。")
    return DockerRuntime(status["endpoint"])


@arena.get("/")
def home():
    projects = BuildStore(current_app.instance_path).list_projects(session["build_owner"])
    with store().edit(session["build_owner"]) as state:
        if not state["targets"]:
            fill_targets(state, rng())
        state["view"] = secrets.token_hex(16)
        if state["defend"]:
            state["defend"]["last_pulse"] = None
        initial = public_state(state)
    return render_template("arena.html", initial=initial, projects=projects,
                           scenarios=DEFEND_SCENARIOS, csrf=session["build_csrf"],
                           runtime=runtime_status(current_app.config["BUILD_DOCKER_ENABLED"]))


@arena.post("/action")
def action():
    data = request.get_json()
    if not isinstance(data, dict):
        raise ValueError("JSON形式の操作を送ってください。")
    if not run_lock.acquire(blocking=False):
        return jsonify(error="実行中です。完了後にもう一度操作してください。"), 409
    try:
        with store().edit(session["build_owner"]) as state:
            command = data.get("action")
            if command == "difficulty":
                value = data.get("value")
                if value not in DIFFICULTIES:
                    raise ValueError("難易度を選択してください。")
                if value != state["difficulty"]:
                    state.update(difficulty=value, attack=None, defend=None)
                    fill_targets(state, rng())
                    if value == "hard":
                        projects = BuildStore(current_app.instance_path).list_projects(session["build_owner"])
                        if projects:
                            project = BuildStore(current_app.instance_path).get(session["build_owner"], projects[0]["id"])
                            if "app.py" in project["files"]:
                                snapshot_defend(state, project, "repeated-reads", "/", rng(), delay())
            elif command == "attack-select":
                begin_attack(state, data.get("target"))
            elif command == "attack-request":
                attack_request(state, data, runtime(), rng())
            elif command == "attack-finish":
                if not state["attack"] or state["attack"]["id"] != data.get("attempt"):
                    raise ValueError("現在の挑戦を確認してください。")
                finish_attack(state, False, rng())
            elif command == "defend-copy":
                project_id = data.get("project")
                if not isinstance(project_id, str):
                    raise ValueError("Buildプロジェクトを選んでください。")
                project = BuildStore(current_app.instance_path).get(session["build_owner"], project_id)
                snapshot_defend(state, project, data.get("scenario"), data.get("path", "/"), rng(), delay())
            elif command == "defend-start":
                if state["difficulty"] == "hard":
                    raise ValueError("HARDでは表示中に攻撃イベントが発生します。")
                if not state["defend"] or state["defend"]["id"] != data.get("attempt"):
                    raise ValueError("現在のコピーを確認してください。")
                start_defend(state, runtime())
            elif command == "defend-assess":
                assess_defend(state, data, runtime())
            elif command == "hint":
                mode = data.get("mode")
                if state["difficulty"] != "easy" or mode not in ("attack", "defend"):
                    raise ValueError("挑戦中の支援はEASYだけで利用できます。")
                attempt = state[mode]
                if attempt is None:
                    raise ValueError("先に演習を選択してください。")
                attempt["hint"] = min(attempt["hint"] + 1, 2)
            elif command == "pulse":
                now = current_app.config.get("ARENA_CLOCK", time.time)()
                if pulse_due(state, data.get("view"), now, data.get("paused") is True):
                    start_defend(state, runtime())
            else:
                raise ValueError("不明な操作です。")
            result = public_state(state)
        return jsonify(state=result)
    finally:
        run_lock.release()
