"""正式第8・9訓練の教材、採点、解放順、DEV進行を確認する。"""

import pytest

from src.answer_check import is_correct
from src.app import app
from src.learn_data import COURSES
from src.learn_routes import FORMAL_COURSE_IDS


NEW_IDS = ("database_sql", "git_dev")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def unlock_through(client, course_id):
    """先行訓練は既存テストで確認済みなので、対象訓練の入口だけを準備する。"""
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            prior_id: {"course_complete": True}
            for prior_id in FORMAL_COURSE_IDS[:FORMAL_COURSE_IDS.index(course_id)]
        }


def answer_for(question):
    if question.get("type") == "true_false":
        return question["answer"]
    if question.get("type") == "term":
        return question["answer"]
    return str(question["answer"])


def play_unit(client, course_id, lesson, *, shortcut=False, wrong_at=None):
    lesson_id = lesson["id"]
    assert client.post(f"/learn/{course_id}/{lesson_id}/start").status_code == 302
    for index, question in enumerate(lesson["questions"]):
        data = {"question_index": str(index)}
        if shortcut:
            data["action"] = "dev_skip"
        elif index == wrong_at:
            data["answer"] = str((question["answer"] + 1) % 4)
        else:
            data["answer"] = answer_for(question)
        response = client.post(f"/learn/{course_id}/{lesson_id}/answer", data=data)
        assert response.status_code == 302
        response = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return response


def play_boss(client, course_id, *, shortcut=False, wrong_at=None):
    course = COURSES[course_id]
    assert client.post(f"/learn/{course_id}/boss/start").status_code == 302
    for index, question in enumerate(course["boss"]):
        answer = answer_for(question)
        if index == wrong_at:
            answer = "false" if answer == "true" else "true" if answer == "false" else "wrong"
        data = {"question_index": str(index), "answer": answer}
        if shortcut:
            data = {"question_index": str(index), "action": "dev_skip"}
        response = client.post(f"/learn/{course_id}/boss/answer", data=data)
        assert response.status_code == 302
        response = client.post(f"/learn/{course_id}/boss/next")
    return response


@pytest.mark.parametrize("course_id,unit_count", [("database_sql", 10), ("git_dev", 11)])
def test_course_structure_and_question_answers(course_id, unit_count):
    course = COURSES[course_id]
    assert len(course["lessons"]) == unit_count
    assert len(course["boss"]) == 14
    assert course["question_mode"] == "choice"
    for lesson in course["lessons"]:
        assert len(lesson["questions"]) == 4
        assert lesson["objective"] and lesson["why"] and lesson["connection"]
        assert len(lesson["sections"]) >= 3
        assert any(
            block["type"] == "key_points"
            for part in lesson["sections"] for block in part["blocks"]
        )
        for question in lesson["questions"]:
            assert len(question["options"]) == 4
            assert question["explanation"]
            assert is_correct(course_id, question, answer_for(question))
            assert len(question["wrong_explanations"]) == 3
    for question in course["boss"]:
        assert question["explanation"]
        assert is_correct(course_id, question, answer_for(question))
    assert {"true_false", "term", "application"} <= {
        question["type"] for question in course["boss"]
    }


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_course_locked_until_previous_boss_is_complete(client, course_id):
    assert client.get(f"/learn/{course_id}/").status_code == 403
    unlock_through(client, course_id)
    assert client.get(f"/learn/{course_id}/").status_code == 200


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_all_lessons_render_and_next_unit_is_locked(client, course_id):
    unlock_through(client, course_id)
    course = COURSES[course_id]
    assert client.get(f"/learn/{course_id}/").status_code == 200
    for lesson in course["lessons"]:
        with client.session_transaction() as browser_session:
            progress = browser_session["learn_progress"]
            progress[course_id] = {
                "completed_lessons": [
                    prior["id"] for prior in course["lessons"]
                    if course["lessons"].index(prior) < course["lessons"].index(lesson)
                ]
            }
            browser_session["learn_progress"] = progress
        page = client.get(f"/learn/{course_id}/{lesson['id']}/")
        assert page.status_code == 200
        html = page.get_data(as_text=True)
        assert lesson["objective"] in html
        assert lesson["sections"][0]["heading"] in html
        assert "KEY POINT" in html
        assert "訓練開始" in html
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        progress[course_id] = {"completed_lessons": []}
        browser_session["learn_progress"] = progress
    locked = client.get(f"/learn/{course_id}/{course['lessons'][1]['id']}/")
    assert locked.status_code == 302


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_wrong_answer_does_not_unlock_and_retry_resets_score(client, course_id):
    unlock_through(client, course_id)
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    question = lesson["questions"][0]
    wrong = str((question["answer"] + 1) % 4)
    client.post(f"/learn/{course_id}/{lesson_id}/answer",
                data={"question_index": "0", "answer": wrong})
    page = client.get(f"/learn/{course_id}/{lesson_id}/battle").get_data(as_text=True)
    assert "INCORRECT" in page
    assert question["options"][question["answer"]] in page
    assert question["explanation"] in page
    client.post(f"/learn/{course_id}/{lesson_id}/answer",
                data={"question_index": "0", "answer": answer_for(question)})
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][course_id]["correct_count"] == 0
    client.post(f"/learn/{course_id}/{lesson_id}/next")
    for index, question in enumerate(lesson["questions"][1:], start=1):
        client.post(f"/learn/{course_id}/{lesson_id}/answer",
                    data={"question_index": str(index), "answer": answer_for(question)})
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    assert result.location.endswith(f"/learn/{course_id}/{lesson_id}/result")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["correct_count"] == 3
        assert not progress["completed_lessons"]
    retry = play_unit(client, course_id, lesson)
    assert retry.location.endswith(f"/learn/{course_id}/{lesson_id}/complete")
    assert client.get(f"/learn/{course_id}/{COURSES[course_id]['lessons'][1]['id']}/").status_code == 200


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_all_units_unlock_boss_and_boss_requires_perfect(client, course_id):
    unlock_through(client, course_id)
    course = COURSES[course_id]
    assert client.post(f"/learn/{course_id}/boss/start").location.endswith(
        f"/learn/{course_id}/"
    )
    for lesson in course["lessons"]:
        result = play_unit(client, course_id, lesson)
        assert result.location.endswith(f"/learn/{course_id}/{lesson['id']}/complete")
    first = course["boss"][0]
    client.post(f"/learn/{course_id}/boss/start")
    client.post(f"/learn/{course_id}/boss/answer",
                data={"question_index": "0", "answer": answer_for(first)})
    page = client.get(f"/learn/{course_id}/boss").get_data(as_text=True)
    assert "CORRECT" in page
    assert "BOSS HP" in page
    client.post(f"/learn/{course_id}/boss/answer",
                data={"question_index": "0", "answer": answer_for(first)})
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["boss_hp"] == 13
        assert progress["boss_correct_count"] == 1
    failure = play_boss(client, course_id, wrong_at=0)
    assert failure.location.endswith(f"/learn/{course_id}/boss/result")
    with client.session_transaction() as browser_session:
        assert not browser_session["learn_progress"][course_id]["course_complete"]
    success = play_boss(client, course_id)
    assert success.location.endswith(f"/learn/{course_id}/complete")
    assert "修了" in client.get(success.location).get_data(as_text=True)


def test_eight_unlocks_nine_and_nine_unlocks_ten(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    unlock_through(client, "database_sql")
    assert client.get("/learn/git_dev/").status_code == 403
    for course_id in NEW_IDS:
        course = COURSES[course_id]
        for lesson in course["lessons"]:
            result = play_unit(client, course_id, lesson, shortcut=True)
            assert result.location.endswith(f"/learn/{course_id}/{lesson['id']}/complete")
        result = play_boss(client, course_id, shortcut=True)
        assert result.location.endswith(f"/learn/{course_id}/complete")
        assert len(result.headers.get("Set-Cookie", "")) < 4096
    assert client.get("/learn/git_dev/").status_code == 200
    page = client.get("/learn/git_dev/complete").get_data(as_text=True)
    assert "セキュリティ基礎訓練" in page
    assert "/learn/security_basics/" in page
    assert client.get("/learn/security_basics/").status_code == 200


def test_dev_button_hidden_when_disabled(client, monkeypatch):
    unlock_through(client, "database_sql")
    lesson_id = COURSES["database_sql"]["lessons"][0]["id"]
    client.post(f"/learn/database_sql/{lesson_id}/start")
    page = client.get(f"/learn/database_sql/{lesson_id}/battle").get_data(as_text=True)
    assert "開発用：この問題を正解扱いにする" not in page
    client.post(f"/learn/database_sql/{lesson_id}/answer",
                data={"question_index": "0", "action": "dev_skip"})
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"]["database_sql"]["correct_count"] == 0


def test_sql_and_git_examples_are_display_only_and_escaped(client, monkeypatch):
    unlock_through(client, "git_dev")
    sql_page = client.get("/learn/database_sql/web_db/")
    assert sql_page.status_code == 302  # UNIT未解放
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        progress["database_sql"] = {
            "completed_lessons": [item["id"] for item in COURSES["database_sql"]["lessons"]],
            "course_complete": True,
        }
        progress["git_dev"] = {
            "completed_lessons": [item["id"] for item in COURSES["git_dev"]["lessons"]]
        }
        browser_session["learn_progress"] = progress
    sql_lesson = next(item for item in COURSES["database_sql"]["lessons"] if item["id"] == "select")
    example = next(
        block for part in sql_lesson["sections"] for block in part["blocks"]
        if block["type"] == "code"
    )
    monkeypatch.setitem(example, "code", "SELECT '<script>alert(1)</script>' FROM users;")
    sql_page = client.get("/learn/database_sql/select/").get_data(as_text=True)
    git_page = client.get("/learn/git_dev/gitignore/").get_data(as_text=True)
    assert "SELECT" in sql_page
    assert "&lt;script&gt;" in sql_page
    assert "<script>alert(1)</script>" not in sql_page
    assert ".gitignore" in git_page
