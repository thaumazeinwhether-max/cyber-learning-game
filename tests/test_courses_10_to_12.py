"""正式第10〜12訓練の教材、進行、防御問題、Learn修了を確認する。"""

import pytest

from src.answer_check import is_correct
from src.app import app
from src.learn_data import COURSES
from src.learn_routes import FORMAL_COURSE_IDS


NEW_IDS = ("security_basics", "web_security", "incident_response")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def unlock_prior(client, course_id):
    """以前の訓練は既存テストに任せ、対象コースの入口を準備する。"""
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            prior_id: {"course_complete": True}
            for prior_id in FORMAL_COURSE_IDS[:FORMAL_COURSE_IDS.index(course_id)]
        }


def correct_answer(question):
    if question["type"] in ("term", "true_false"):
        return question["answer"]
    return str(question["answer"])


def wrong_answer(question):
    if question["type"] == "true_false":
        return "false" if question["answer"] == "true" else "true"
    if question["type"] == "term":
        return "incorrect term"
    return str((question["answer"] + 1) % 4)


def finish_unit(client, course_id, lesson, *, shortcut=False, wrong_index=None):
    lesson_id = lesson["id"]
    assert client.post(f"/learn/{course_id}/{lesson_id}/start").status_code == 302
    for index, question in enumerate(lesson["questions"]):
        data = {"question_index": str(index)}
        if shortcut:
            data["action"] = "dev_skip"
        else:
            data["answer"] = (
                wrong_answer(question) if index == wrong_index else correct_answer(question)
            )
        assert client.post(
            f"/learn/{course_id}/{lesson_id}/answer", data=data
        ).status_code == 302
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return result


def finish_boss(client, course_id, *, shortcut=False, wrong_index=None):
    course = COURSES[course_id]
    assert client.post(f"/learn/{course_id}/boss/start").status_code == 302
    for index, question in enumerate(course["boss"]):
        data = {"question_index": str(index)}
        if shortcut:
            data["action"] = "dev_skip"
        else:
            data["answer"] = (
                wrong_answer(question) if index == wrong_index else correct_answer(question)
            )
        assert client.post(f"/learn/{course_id}/boss/answer", data=data).status_code == 302
        result = client.post(f"/learn/{course_id}/boss/next")
    return result


@pytest.mark.parametrize("course_id,boss_size", [
    ("security_basics", 15), ("web_security", 15), ("incident_response", 16),
])
def test_curriculum_data_and_answers(course_id, boss_size):
    course = COURSES[course_id]
    assert len(course["lessons"]) == 11
    assert len(course["boss"]) == boss_size
    assert course["question_mode"] == "choice"
    for lesson in course["lessons"]:
        assert len(lesson["questions"]) == 4
        assert lesson["objective"] and lesson["why"] and lesson["connection"]
        assert len(lesson["sections"]) == 3
        assert any(
            block["type"] == "key_points"
            for part in lesson["sections"] for block in part["blocks"]
        )
        for question in lesson["questions"]:
            if question["type"] == "true_false":
                assert question["answer"] in ("true", "false")
            else:
                assert len(question["options"]) == 4
            assert question["explanation"]
            assert is_correct(course_id, question, correct_answer(question))
            assert not is_correct(course_id, question, wrong_answer(question))
    for question in course["boss"]:
        assert question["explanation"]
        assert is_correct(course_id, question, correct_answer(question))
        assert not is_correct(course_id, question, wrong_answer(question))
    assert {"application", "term", "true_false"} <= {
        question["type"] for question in course["boss"]
    }
    assert any(
        question["type"] == "true_false"
        for lesson in course["lessons"] for question in lesson["questions"]
    )


@pytest.mark.parametrize("course_id,unit_id", [
    ("security_basics", "cia"),
    ("web_security", "session"),
    ("incident_response", "anomaly"),
])
def test_normal_true_false_question_renders_and_scores(client, course_id, unit_id):
    unlock_prior(client, course_id)
    course = COURSES[course_id]
    target_index = next(
        index for index, lesson in enumerate(course["lessons"])
        if lesson["id"] == unit_id
    )
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        progress[course_id] = {
            "completed_lessons": [
                lesson["id"] for lesson in course["lessons"][:target_index]
            ]
        }
        browser_session["learn_progress"] = progress
    lesson = course["lessons"][target_index]
    assert lesson["questions"][-1]["type"] == "true_false"
    client.post(f"/learn/{course_id}/{unit_id}/start")
    for index, question in enumerate(lesson["questions"][:-1]):
        client.post(f"/learn/{course_id}/{unit_id}/answer", data={
            "question_index": str(index), "answer": correct_answer(question),
        })
        client.post(f"/learn/{course_id}/{unit_id}/next")
    page = client.get(f"/learn/{course_id}/{unit_id}/battle").get_data(as_text=True)
    assert "○ 正しい" in page and "× 間違っている" in page
    question = lesson["questions"][-1]
    client.post(f"/learn/{course_id}/{unit_id}/answer", data={
        "question_index": "3", "answer": wrong_answer(question),
    })
    result = client.get(f"/learn/{course_id}/{unit_id}/battle").get_data(as_text=True)
    assert "INCORRECT" in result
    assert question["explanation"] in result


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_course_lock_and_all_unit_pages(client, course_id):
    assert client.get(f"/learn/{course_id}/").status_code == 403
    unlock_prior(client, course_id)
    course = COURSES[course_id]
    assert client.get(f"/learn/{course_id}/").status_code == 200
    assert client.get(
        f"/learn/{course_id}/{course['lessons'][1]['id']}/"
    ).status_code == 302
    for index, lesson in enumerate(course["lessons"]):
        with client.session_transaction() as browser_session:
            progress = browser_session["learn_progress"]
            progress[course_id] = {
                "completed_lessons": [
                    prior["id"] for prior in course["lessons"][:index]
                ],
            }
            browser_session["learn_progress"] = progress
        page = client.get(f"/learn/{course_id}/{lesson['id']}/")
        assert page.status_code == 200
        html = page.get_data(as_text=True)
        assert lesson["objective"] in html
        assert lesson["sections"][0]["heading"] in html
        assert "KEY POINT" in html
        assert "訓練開始" in html


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_one_answer_then_result_and_full_retry(client, course_id):
    unlock_prior(client, course_id)
    course = COURSES[course_id]
    lesson = course["lessons"][0]
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    first = lesson["questions"][0]
    answer_url = f"/learn/{course_id}/{lesson_id}/answer"
    client.post(answer_url, data={
        "question_index": "0", "answer": wrong_answer(first),
    })
    page = client.get(f"/learn/{course_id}/{lesson_id}/battle").get_data(as_text=True)
    assert "INCORRECT" in page
    assert first["options"][first["answer"]] in page
    assert first["explanation"] in page
    client.post(answer_url, data={
        "question_index": "0", "answer": correct_answer(first),
    })
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][course_id]["correct_count"] == 0
    client.post(f"/learn/{course_id}/{lesson_id}/next")
    for index, question in enumerate(lesson["questions"][1:], start=1):
        client.post(answer_url, data={
            "question_index": str(index), "answer": correct_answer(question),
        })
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    assert result.location.endswith(f"/learn/{course_id}/{lesson_id}/result")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["correct_count"] == 3
        assert lesson_id not in progress["completed_lessons"]
    assert client.get(
        f"/learn/{course_id}/{course['lessons'][1]['id']}/"
    ).status_code == 302
    retry = finish_unit(client, course_id, lesson)
    assert retry.location.endswith(f"/learn/{course_id}/{lesson_id}/complete")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["correct_count"] == 4
        assert lesson_id in progress["completed_lessons"]


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_boss_requires_all_units_and_perfect_score(client, course_id):
    unlock_prior(client, course_id)
    course = COURSES[course_id]
    assert client.post(f"/learn/{course_id}/boss/start").location.endswith(
        f"/learn/{course_id}/"
    )
    for lesson in course["lessons"]:
        result = finish_unit(client, course_id, lesson)
        assert result.location.endswith(f"/learn/{course_id}/{lesson['id']}/complete")
    assert client.post(f"/learn/{course_id}/boss/start").status_code == 302
    first = course["boss"][0]
    client.post(f"/learn/{course_id}/boss/answer", data={
        "question_index": "0", "answer": correct_answer(first),
    })
    page = client.get(f"/learn/{course_id}/boss").get_data(as_text=True)
    assert "CORRECT" in page and "BOSS HP" in page
    client.post(f"/learn/{course_id}/boss/answer", data={
        "question_index": "0", "answer": correct_answer(first),
    })
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["boss_correct_count"] == 1
        assert progress["boss_hp"] == len(course["boss"]) - 1
    failure = finish_boss(client, course_id, wrong_index=0)
    assert failure.location.endswith(f"/learn/{course_id}/boss/result")
    with client.session_transaction() as browser_session:
        assert not browser_session["learn_progress"][course_id]["course_complete"]
    success = finish_boss(client, course_id)
    assert success.location.endswith(f"/learn/{course_id}/complete")
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][course_id]["course_complete"]


def test_dev_shortcut_unlocks_ten_eleven_twelve_and_learn_completion(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    unlock_prior(client, "security_basics")
    assert client.get("/learn/web_security/").status_code == 403
    for course_id in NEW_IDS:
        course = COURSES[course_id]
        for lesson in course["lessons"]:
            result = finish_unit(client, course_id, lesson, shortcut=True)
            assert result.location.endswith(f"/learn/{course_id}/{lesson['id']}/complete")
        result = finish_boss(client, course_id, shortcut=True)
        assert result.location.endswith(f"/learn/{course_id}/complete")
        assert len(result.headers.get("Set-Cookie", "")) < 4096
    final_page = client.get("/learn/incident_response/complete").get_data(as_text=True)
    learn_page = client.get("/learn/").get_data(as_text=True)
    assert "INCIDENT RESPONSE TRAINING COMPLETE" in final_page
    assert "LEARN PHASE COMPLETE" in final_page
    assert "LEARN PHASE COMPLETE" in learn_page
    with client.session_transaction() as browser_session:
        assert all(
            browser_session["learn_progress"][course_id]["course_complete"]
            for course_id in NEW_IDS
        )


def test_final_boss_is_only_about_incident_response_units():
    course = COURSES["incident_response"]
    unit_ids = {lesson["id"] for lesson in course["lessons"]}
    assert course["boss_scope"] == "incident_response"
    assert {question["unit_id"] for question in course["boss"]} == unit_ids
    assert all(question["unit_id"] in unit_ids for question in course["boss"])


@pytest.mark.parametrize("course_id,terms", [
    ("security_basics", (
        "CIA", "threat", "vulnerability", "risk", "authentication",
        "authorization", "ハッシュ", "暗号化", "最小権限", "backup",
        "環境変数", "多層防御",
    )),
    ("web_security", (
        "input validation", "parameterized query", "authentication",
        "authorization", "Cookie", "Session", "escaping", "CSRF",
        "stack trace", "ログ", "多層防御",
    )),
    ("incident_response", (
        "baseline", "anomaly", "application log", "access log",
        "error log", "monitoring", "alert", "incident", "初動",
        "影響範囲", "containment", "root cause", "recovery",
        "再発防止", "記録",
    )),
])
def test_required_concepts_appear_in_textbook(course_id, terms):
    course = COURSES[course_id]
    text = " ".join(
        str({
            key: lesson[key]
            for key in ("objective", "why", "connection", "sections")
        })
        for lesson in course["lessons"]
    ).casefold()
    for term in terms:
        assert term.casefold() in text


def test_dev_button_is_hidden_and_cannot_skip_when_disabled(client):
    unlock_prior(client, "security_basics")
    lesson_id = COURSES["security_basics"]["lessons"][0]["id"]
    client.post(f"/learn/security_basics/{lesson_id}/start")
    page = client.get(f"/learn/security_basics/{lesson_id}/battle").get_data(as_text=True)
    assert "DEV MODE" not in page
    assert "開発用：この問題を正解扱いにする" not in page
    client.post(f"/learn/security_basics/{lesson_id}/answer", data={
        "question_index": "0", "action": "dev_skip",
    })
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"]["security_basics"]["correct_count"] == 0


def test_code_block_escapes_html_from_lesson_data(client, monkeypatch):
    unlock_prior(client, "web_security")
    lesson = next(
        item for item in COURSES["web_security"]["lessons"] if item["id"] == "output"
    )
    example = next(
        block for part in lesson["sections"] for block in part["blocks"]
        if block["type"] == "code"
    )
    monkeypatch.setitem(example, "code", "<script>alert(1)</script>")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        progress["web_security"] = {
            "completed_lessons": [
                item["id"] for item in COURSES["web_security"]["lessons"]
            ]
        }
        browser_session["learn_progress"] = progress
    page = client.get("/learn/web_security/output/").get_data(as_text=True)
    assert "&lt;script&gt;" in page
    assert "<script>alert(1)</script>" not in page
