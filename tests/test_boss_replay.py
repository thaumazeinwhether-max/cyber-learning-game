"""BOSSの再挑戦と、アプリ共通テーマの表示を確認する。"""

import pytest

from src.app import app
from src.learn_data import COURSES
from src.learn_routes import FORMAL_COURSE_IDS


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def set_completed_course(client, course_id):
    """修了記録を持つブラウザーを用意する。前の正式訓練も解放済みにする。"""
    course = COURSES[course_id]
    progress = {
        "completed_lessons": [lesson["id"] for lesson in course["lessons"]],
        "course_complete": True,
        "boss_hp": 0,
        "boss_index": len(course["boss"]) - 1,
        "boss_correct_count": len(course["boss"]),
        "boss_answered": True,
        "boss_correct": True,
        "boss_submitted_answer": "previous answer",
        "boss_result": {"passed": True},
    }
    previous_ids = FORMAL_COURSE_IDS[:FORMAL_COURSE_IDS.index(course_id)] if course_id in FORMAL_COURSE_IDS else ()
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            **{previous_id: {"course_complete": True} for previous_id in previous_ids},
            course_id: progress,
        }


@pytest.mark.parametrize("course_id", FORMAL_COURSE_IDS)
def test_every_cleared_formal_boss_can_restart_at_full_hp(client, course_id):
    set_completed_course(client, course_id)
    count = len(COURSES[course_id]["boss"])

    selection = client.get(f"/learn/{course_id}/")
    completion = client.get(f"/learn/{course_id}/complete")
    assert "BOSSに再挑戦" in selection.get_data(as_text=True)
    assert "BOSSに再挑戦" in completion.get_data(as_text=True)

    started = client.post(f"/learn/{course_id}/boss/start", follow_redirects=True)
    page = started.get_data(as_text=True)
    assert started.status_code == 200
    assert f"QUESTION 1 / {count}" in page
    assert f'aria-label="BOSS HP {count} / {count}"' in page
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["course_complete"] is True
        assert progress["completed_lessons"] == [lesson["id"] for lesson in COURSES[course_id]["lessons"]]
        assert progress["boss_index"] == 0
        assert progress["boss_hp"] == count
        assert progress["boss_correct_count"] == 0
        assert progress["boss_answered"] is False
        assert progress["boss_result"] is None
    if course_id != FORMAL_COURSE_IDS[-1]:
        next_id = FORMAL_COURSE_IDS[FORMAL_COURSE_IDS.index(course_id) + 1]
        assert client.get(f"/learn/{next_id}/").status_code == 200


def test_failed_replay_keeps_victory_and_next_training(client, monkeypatch):
    course_id = "computer_os"
    set_completed_course(client, course_id)
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    assert client.post(f"/learn/{course_id}/boss/start").status_code == 302

    for index, _question in enumerate(COURSES[course_id]["boss"]):
        answer = {"question_index": str(index), "action": "dev_skip"}
        if index == 0:
            answer = {"question_index": "0", "answer": "wrong"}
        client.post(f"/learn/{course_id}/boss/answer", data=answer)
        result = client.post(f"/learn/{course_id}/boss/next")

    assert result.location.endswith("/boss/result")
    failed_page = client.get(result.location).get_data(as_text=True)
    assert "BOSS BATTLE FAILED" in failed_page
    assert "過去の訓練修了記録" in failed_page
    assert "修了画面へ" in failed_page
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["boss_result"]["passed"] is False
        assert progress["course_complete"] is True
        assert len(progress["completed_lessons"]) == len(COURSES[course_id]["lessons"])
    assert client.get("/learn/python_basics_1/").status_code == 200
    assert "BOSS DEFEATED" in client.get(f"/learn/{course_id}/complete").get_data(as_text=True)


def test_replay_after_real_victory_can_defeat_boss_again(client):
    course_id = "it"
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            course_id: {"completed_lessons": ["computer", "network", "web"]}
        }

    for attempt in range(2):
        assert client.post(f"/learn/{course_id}/boss/start").location.endswith("/boss")
        for index, answer in enumerate(("false", "DNS", "true")):
            client.post(f"/learn/{course_id}/boss/answer", data={"question_index": str(index), "answer": answer})
            result = client.post(f"/learn/{course_id}/boss/next")
        assert result.location.endswith("/complete")
        assert "BOSS DEFEATED" in client.get(result.location).get_data(as_text=True)
        with client.session_transaction() as browser_session:
            assert browser_session["learn_progress"][course_id]["course_complete"] is True
        if attempt == 0:
            assert "BOSSに再挑戦" in client.get(f"/learn/{course_id}/").get_data(as_text=True)


def test_final_boss_failed_replay_keeps_learn_phase_complete(client, monkeypatch):
    course_id = "incident_response"
    set_completed_course(client, course_id)
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    client.post(f"/learn/{course_id}/boss/start")
    for index, _question in enumerate(COURSES[course_id]["boss"]):
        answer = {"question_index": str(index), "action": "dev_skip"}
        if index == 0:
            answer = {"question_index": "0", "answer": "wrong"}
        client.post(f"/learn/{course_id}/boss/answer", data=answer)
        result = client.post(f"/learn/{course_id}/boss/next")

    assert result.location.endswith("/boss/result")
    assert "LEARN PHASE COMPLETE" in client.get("/learn/").get_data(as_text=True)
    assert "LEARN PHASE COMPLETE" in client.get(f"/learn/{course_id}/complete").get_data(as_text=True)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        assert all(progress[previous]["course_complete"] for previous in FORMAL_COURSE_IDS)
        assert progress[course_id]["boss_result"]["passed"] is False


def test_uncleared_boss_still_requires_finished_units(client):
    assert client.post("/learn/computer_os/boss/start").location.endswith("/learn/computer_os/")
    assert client.get("/learn/computer_os/boss").location.endswith("/learn/computer_os/")


def test_old_cookie_with_victory_record_can_replay(client):
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {"it": {"course_complete": True}}

    started = client.post("/learn/it/boss/start", follow_redirects=True)
    assert started.status_code == 200
    assert "QUESTION 1 / 3" in started.get_data(as_text=True)
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"]["it"]["course_complete"] is True


def test_existing_pages_share_hud_theme(client):
    set_completed_course(client, "it")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]["it"]
        progress["active_lesson"] = "computer"
        progress["question_index"] = 0
        progress["attempt_result"] = {"lesson_id": "computer", "correct_count": 1, "total": 2, "passed": False}
        progress["boss_started"] = True
        progress["boss_index"] = 0
        progress["boss_result"] = {"correct_count": 2, "total": 3, "hp": 1, "passed": False}
        browser_session["learn_progress"] = {"it": progress}

    pages = (
        "/", "/learn/", "/learn/it/", "/learn/it/computer/",
        "/learn/it/computer/battle", "/learn/it/computer/result",
        "/learn/it/computer/complete", "/learn/it/boss",
        "/learn/it/boss/result", "/learn/it/complete",
    )
    for path in pages:
        response = client.get(path)
        assert response.status_code == 200, path
        assert 'class="hud-interface ' in response.get_data(as_text=True), path
    top = client.get("/").get_data(as_text=True)
    assert "Build" in top and "Attack &amp; Defend" in top
    assert 'href="/arena/"' in top
    assert 'href="/build/"' in top
