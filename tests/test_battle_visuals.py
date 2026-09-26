"""表示上の敵HPとバトル画面。正誤と進捗の判定は既存テストも確認する。"""

import pytest

from src.app import app
from src.learn_data import COURSES
from src.learn_routes import FORMAL_COURSE_IDS


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def unlock_course(client, course_id):
    index = FORMAL_COURSE_IDS.index(course_id)
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            previous: {"course_complete": True}
            for previous in FORMAL_COURSE_IDS[:index]
        }


def answer_one(client, course_id, lesson_id, index, answer):
    return client.post(
        f"/learn/{course_id}/{lesson_id}/answer",
        data={"question_index": str(index), "answer": answer},
        follow_redirects=True,
    ).get_data(as_text=True)


@pytest.mark.parametrize("course_id", FORMAL_COURSE_IDS)
def test_each_formal_course_uses_drone_field_and_question_count_hp(client, course_id):
    unlock_course(client, course_id)
    lesson = COURSES[course_id]["lessons"][0]
    client.post(f"/learn/{course_id}/{lesson['id']}/start")
    page = client.get(f"/learn/{course_id}/{lesson['id']}/battle").get_data(as_text=True)
    question_count = len(lesson["questions"])
    assert 'aria-label="バトルフィールド"' in page
    assert 'class="drone-art"' in page
    assert 'class="robot-art"' not in page
    assert f'aria-label="ドローン HP {question_count} / {question_count}"' in page
    assert f'aria-valuemax="{question_count}"' in page
    assert f'aria-valuenow="{question_count}"' in page
    assert "QUESTION 1 /" in page
    assert "回答する" in page


def test_drone_hit_miss_and_final_defeat(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    course_id = "computer_os"
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    count = len(lesson["questions"])
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    first = answer_one(client, course_id, lesson_id, 0, str(lesson["questions"][0]["answer"]))
    assert f'aria-label="ドローン HP {count - 1} / {count}"' in first
    assert "HIT / ドローンに命中" in first
    assert "ENEMY DEFEATED" not in first
    client.post(f"/learn/{course_id}/{lesson_id}/next")
    for index in range(1, count):
        page = client.post(
            f"/learn/{course_id}/{lesson_id}/answer",
            data={"question_index": str(index), "action": "dev_skip"},
            follow_redirects=True,
        ).get_data(as_text=True)
        if index < count - 1:
            assert "ENEMY DEFEATED" not in page
            client.post(f"/learn/{course_id}/{lesson_id}/next")
    assert f'aria-label="ドローン HP 0 / {count}"' in page
    assert "ENEMY DEFEATED" in page
    complete = client.post(f"/learn/{course_id}/{lesson_id}/next", follow_redirects=True)
    assert "UNIT COMPLETE" in complete.get_data(as_text=True)
    assert "ENEMY DEFEATED" in complete.get_data(as_text=True)


def test_wrong_answer_keeps_drone_hp_and_failed_result(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    course_id = "computer_os"
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    count = len(lesson["questions"])
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    wrong_index = (lesson["questions"][0]["answer"] + 1) % 4
    first = answer_one(client, course_id, lesson_id, 0, str(wrong_index))
    assert f'aria-label="ドローン HP {count} / {count}"' in first
    assert "INCOMING FIRE" in first
    client.post(f"/learn/{course_id}/{lesson_id}/next")
    for index in range(1, count):
        client.post(f"/learn/{course_id}/{lesson_id}/answer", data={"question_index": str(index), "action": "dev_skip"})
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    assert result.location.endswith("/result")
    page = client.get(result.location).get_data(as_text=True)
    assert "DRONE HP 1 / 6" in page
    assert "BATTLE FAILED" in page


def test_boss_robot_hp_hit_miss_and_result(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    course_id = "computer_os"
    course = COURSES[course_id]
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            course_id: {"completed_lessons": [lesson["id"] for lesson in course["lessons"]]}
        }
    client.post(f"/learn/{course_id}/boss/start")
    count = len(course["boss"])
    start = client.get(f"/learn/{course_id}/boss").get_data(as_text=True)
    assert "BOSS BATTLE" in start
    assert 'class="robot-art"' in start
    assert f'aria-label="BOSS HP {count} / {count}"' in start
    wrong = client.post(f"/learn/{course_id}/boss/answer", data={"question_index": "0", "answer": "invalid"}, follow_redirects=True).get_data(as_text=True)
    assert f'aria-label="BOSS HP {count} / {count}"' in wrong
    assert "INCOMING FIRE" in wrong
    client.post(f"/learn/{course_id}/boss/next")
    for index in range(1, count):
        client.post(f"/learn/{course_id}/boss/answer", data={"question_index": str(index), "action": "dev_skip"})
        result = client.post(f"/learn/{course_id}/boss/next")
    assert result.location.endswith("/boss/result")
    page = client.get(result.location).get_data(as_text=True)
    assert f'aria-label="BOSS HP 1 / {count}"' in page
    assert "BOSS BATTLE FAILED" in page
    client.post(f"/learn/{course_id}/boss/start")
    first_hit = client.post(f"/learn/{course_id}/boss/answer", data={"question_index": "0", "action": "dev_skip"}, follow_redirects=True).get_data(as_text=True)
    assert f'aria-label="BOSS HP {count - 1} / {count}"' in first_hit
    client.post(f"/learn/{course_id}/boss/next")
    for index in range(1, count):
        page = client.post(f"/learn/{course_id}/boss/answer", data={"question_index": str(index), "action": "dev_skip"}, follow_redirects=True).get_data(as_text=True)
        if index < count - 1:
            client.post(f"/learn/{course_id}/boss/next")
    assert f'aria-label="BOSS HP 0 / {count}"' in page
    assert "BOSS DEFEATED" in page
    complete = client.post(f"/learn/{course_id}/boss/next", follow_redirects=True).get_data(as_text=True)
    assert "BOSS DEFEATED" in complete
    assert "COURSE COMPLETE" in complete or "COMPUTER & OS TRAINING COMPLETE" in complete
