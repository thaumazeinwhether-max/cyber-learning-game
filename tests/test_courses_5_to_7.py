"""正式第5〜7訓練の表示、採点、進行、DEVショートカット。"""

import pytest

from src.answer_check import is_correct
from src.app import app
from src.learn_data import COURSES


FORMAL_IDS = (
    "computer_os", "python_basics_1", "network_basics", "web_http",
    "python_basics_2", "web_creation", "flask_basics",
)
NEW_IDS = FORMAL_IDS[4:]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def unlock_previous(client, course_id):
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            prior_id: {"course_complete": True}
            for prior_id in FORMAL_IDS[:FORMAL_IDS.index(course_id)]
        }


def normal_answer(course_id, question):
    if question.get("mode", COURSES[course_id]["question_mode"]) == "choice":
        return str(question["answer"])
    return question["answer"]


def finish_unit(client, course_id, lesson, shortcut=False):
    lesson_id = lesson["id"]
    start = client.post(f"/learn/{course_id}/{lesson_id}/start")
    assert start.status_code == 302
    for number, question in enumerate(lesson["questions"]):
        data = {"question_index": str(number)}
        if shortcut:
            data["action"] = "dev_skip"
        else:
            data["answer"] = normal_answer(course_id, question)
        client.post(f"/learn/{course_id}/{lesson_id}/answer", data=data)
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return result


def boss_answer(course_id, question, index, shortcut=False):
    data = {"question_index": str(index)}
    if shortcut:
        data["action"] = "dev_skip"
    elif question.get("mode", COURSES[course_id]["question_mode"]) == "choice":
        data["answer"] = str(question["answer"])
    else:
        data["answer"] = "correct" if question["valid"] else "incorrect"
        if not question["valid"]:
            data["corrected_code"] = question["answer"]
    return data


def finish_course(client, course_id, shortcut=False):
    course = COURSES[course_id]
    for lesson in course["lessons"]:
        result = finish_unit(client, course_id, lesson, shortcut)
        assert result.location.endswith(f"/learn/{course_id}/{lesson['id']}/complete")
    start = client.post(f"/learn/{course_id}/boss/start")
    assert start.location.endswith(f"/learn/{course_id}/boss")
    for index, question in enumerate(course["boss"]):
        data = boss_answer(course_id, question, index, shortcut)
        client.post(f"/learn/{course_id}/boss/answer", data=data)
        result = client.post(f"/learn/{course_id}/boss/next")
    return result


@pytest.mark.parametrize("course_id,unit_count,boss_count", [
    ("python_basics_2", 10, 14),
    ("web_creation", 10, 14),
    ("flask_basics", 12, 14),
])
def test_new_curriculum_structure_and_answers(course_id, unit_count, boss_count):
    course = COURSES[course_id]
    assert len(course["lessons"]) == unit_count
    assert len(course["boss"]) == boss_count
    for lesson in course["lessons"]:
        assert 4 <= len(lesson["questions"]) <= 5
        assert lesson["objective"] and lesson["why"] and lesson["connection"]
        assert len(lesson["sections"]) >= 3
        blocks = [block for section in lesson["sections"] for block in section["blocks"]]
        assert {"paragraph", "key_points"} <= {block["type"] for block in blocks}
        assert any(block["type"] in ("code", "table", "flow") for block in blocks)
        for question in lesson["questions"]:
            assert question["explanation"]
            if question.get("mode", course["question_mode"]) == "choice":
                assert len(question["options"]) == 4
            assert is_correct(course_id, question, normal_answer(course_id, question))
    for question in course["boss"]:
        assert question["explanation"]
        if question.get("mode", course["question_mode"]) == "choice":
            assert is_correct(course_id, question, str(question["answer"]))
        else:
            assert is_correct(
                course_id, question, "correct" if question["valid"] else "incorrect",
                "" if question["valid"] else question["answer"],
            )


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_locked_then_all_unit_pages_and_normal_progress(client, course_id):
    assert client.get(f"/learn/{course_id}/").status_code == 403
    assert client.post(f"/learn/{course_id}/boss/start").status_code == 403
    unlock_previous(client, course_id)
    course = COURSES[course_id]
    assert client.get(f"/learn/{course_id}/").status_code == 200
    assert client.get(f"/learn/{course_id}/{course['lessons'][1]['id']}/").status_code == 302
    for lesson in course["lessons"]:
        lesson_id = lesson["id"]
        page = client.get(f"/learn/{course_id}/{lesson_id}/")
        assert page.status_code == 200
        text = page.get_data(as_text=True)
        assert lesson["objective"] in text
        assert "前のUNITとの接続" in text
        assert "これだけ覚えよう" in text
        assert "訓練開始" in text
        finish_unit(client, course_id, lesson)
    assert client.post(f"/learn/{course_id}/boss/start").location.endswith(
        f"/learn/{course_id}/boss"
    )


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_wrong_answer_explanation_no_retry_and_full_reset(client, course_id):
    unlock_previous(client, course_id)
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    for index, question in enumerate(lesson["questions"]):
        if index == 0:
            wrong = "invalid code!" if course_id == "python_basics_2" else str((question["answer"] + 1) % 4)
            answer = wrong
        else:
            answer = normal_answer(course_id, question)
        response = client.post(f"/learn/{course_id}/{lesson_id}/answer",
                               data={"question_index": str(index), "answer": answer},
                               follow_redirects=True)
        if index == 0:
            text = response.get_data(as_text=True)
            assert "INCORRECT / ATTACK FAILED" in text
            assert question["explanation"] in text
            assert "次の問題へ" in text
            if course_id != "python_basics_2":
                assert "回答を見直すポイント" in text
            # 回答済みの問題では同じ回答フォームを再表示しない。
            assert f'action="/learn/{course_id}/{lesson_id}/answer"' not in text
            client.post(f"/learn/{course_id}/{lesson_id}/answer",
                        data={"question_index": "0", "answer": normal_answer(course_id, question)})
        client.post(f"/learn/{course_id}/{lesson_id}/next")
    result = client.get(f"/learn/{course_id}/{lesson_id}/result").get_data(as_text=True)
    assert "UNIT CLEAR FAILED" in result
    assert "3 / 4" in result
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert lesson_id not in progress["completed_lessons"]
        assert progress["correct_count"] == 3
    assert client.get(f"/learn/{course_id}/{COURSES[course_id]['lessons'][1]['id']}/").status_code == 302
    finish_unit(client, course_id, lesson)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert lesson_id in progress["completed_lessons"]
        assert progress["correct_count"] == 4


def test_python_2_ast_alternatives_and_rejection():
    course = COURSES["python_basics_2"]
    while_question = course["lessons"][1]["questions"][0]
    alternative = "count = 0\nwhile count < 3:\n    print(count)\n    count += 1"
    assert is_correct("python_basics_2", while_question, alternative)
    assert not is_correct("python_basics_2", while_question, "while True:\n    pass")
    assert not is_correct("python_basics_2", while_question, "open('x', 'w')")
    dict_question = course["lessons"][3]["questions"][0]
    assert is_correct("python_basics_2", dict_question, "user = {'score': 100, 'name': 'Alice'}")
    boss = course["boss"][2]
    assert is_correct("python_basics_2", boss, "incorrect", alternative)


def test_web_creation_code_reading_and_html_escape(client):
    unlock_previous(client, "web_creation")
    lesson = COURSES["web_creation"]["lessons"][0]
    client.post(f"/learn/web_creation/{lesson['id']}/start")
    client.post("/learn/web_creation/html/answer",
                data={"question_index": "0", "answer": str(lesson["questions"][0]["answer"])})
    client.post("/learn/web_creation/html/next")
    page = client.get("/learn/web_creation/html/battle").get_data(as_text=True)
    assert "&lt;p&gt;Hello&lt;/p&gt;" in page
    assert "<p>Hello</p>" not in page
    assert "答えを1つ選ぶ" in page


def test_flask_mixed_questions_and_boss_modes(client):
    unlock_previous(client, "flask_basics")
    course = COURSES["flask_basics"]
    assert {question.get("mode", "code") for lesson in course["lessons"]
            for question in lesson["questions"]} == {"code", "choice"}
    assert {question.get("mode", "code") for question in course["boss"]} == {"code", "choice"}
    assert any("render_template" in question.get("code", "") or
               "render_template" in question.get("answer", "")
               for question in course["boss"] if question.get("mode", "code") == "code")
    result = finish_course(client, "flask_basics")
    assert result.location.endswith("/learn/flask_basics/complete")


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_normal_answers_defeat_boss_and_unlock_next(client, course_id):
    unlock_previous(client, course_id)
    result = finish_course(client, course_id)
    assert result.location.endswith(f"/learn/{course_id}/complete")
    complete = client.get(result.location)
    assert complete.status_code == 200
    assert COURSES[course_id]["title"] in complete.get_data(as_text=True)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["course_complete"]
        assert progress["boss_hp"] == 0
    index = FORMAL_IDS.index(course_id)
    if index + 1 < len(FORMAL_IDS):
        assert client.get(f"/learn/{FORMAL_IDS[index + 1]}/").status_code == 200


def test_flask_boss_switches_between_code_review_and_choice(client):
    unlock_previous(client, "flask_basics")
    course_id = "flask_basics"
    for lesson in COURSES[course_id]["lessons"]:
        finish_unit(client, course_id, lesson)
    client.post(f"/learn/{course_id}/boss/start")
    first = client.get(f"/learn/{course_id}/boss").get_data(as_text=True)
    assert "このコードは正しいか？" in first
    data = boss_answer(course_id, COURSES[course_id]["boss"][0], 0)
    client.post(f"/learn/{course_id}/boss/answer", data=data)
    client.post(f"/learn/{course_id}/boss/answer", data=data)
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][course_id]["boss_hp"] == 13
    client.post(f"/learn/{course_id}/boss/next")
    second = COURSES[course_id]["boss"][1]
    client.post(f"/learn/{course_id}/boss/answer", data=boss_answer(course_id, second, 1))
    client.post(f"/learn/{course_id}/boss/next")
    third = client.get(f"/learn/{course_id}/boss").get_data(as_text=True)
    assert "答えを1つ選ぶ" in third
    assert "このコードは正しいか？" not in third


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_boss_one_wrong_keeps_course_locked(client, course_id):
    unlock_previous(client, course_id)
    course = COURSES[course_id]
    for lesson in course["lessons"]:
        finish_unit(client, course_id, lesson)
    client.post(f"/learn/{course_id}/boss/start")
    for index, question in enumerate(course["boss"]):
        data = boss_answer(course_id, question, index)
        if index == 0:
            if question.get("mode", course["question_mode"]) == "choice":
                if question.get("type") == "true_false":
                    data["answer"] = "false" if question["answer"] == "true" else "true"
                else:
                    data["answer"] = str((question["answer"] + 1) % 4)
            else:
                data = {"question_index": "0", "answer": "incorrect" if question["valid"] else "correct"}
        client.post(f"/learn/{course_id}/boss/answer", data=data)
        result = client.post(f"/learn/{course_id}/boss/next")
    assert result.location.endswith(f"/learn/{course_id}/boss/result")
    with client.session_transaction() as browser_session:
        assert not browser_session["learn_progress"][course_id]["course_complete"]


def test_dev_completes_five_six_seven_and_unlocks_eight(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    unlock_previous(client, "python_basics_2")
    for course_id in NEW_IDS:
        result = finish_course(client, course_id, shortcut=True)
        assert result.location.endswith(f"/learn/{course_id}/complete")
        assert client.get(f"/learn/{course_id}/complete").status_code == 200
        with client.session_transaction() as browser_session:
            assert browser_session["learn_progress"][course_id]["course_complete"]
    page = client.get("/learn/flask_basics/complete").get_data(as_text=True)
    assert "データベース・SQL基礎" in page
    assert "/learn/database_sql/" in page
    assert client.get("/learn/flask_basics/").status_code == 200
    assert client.get("/learn/database_sql/").status_code == 200


def test_one_browser_can_finish_all_seven_courses(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    for course_id in FORMAL_IDS:
        result = finish_course(client, course_id, shortcut=True)
        assert result.location.endswith(f"/learn/{course_id}/complete")
        assert len(result.headers.get("Set-Cookie", "")) < 4096
    with client.session_transaction() as browser_session:
        assert all(
            browser_session["learn_progress"][course_id]["course_complete"]
            for course_id in FORMAL_IDS
        )


def test_dev_button_hidden_without_environment(client, monkeypatch):
    unlock_previous(client, "python_basics_2")
    client.post("/learn/python_basics_2/for_range/start")
    page = client.get("/learn/python_basics_2/for_range/battle").get_data(as_text=True)
    assert "開発用：この問題を正解扱いにする" not in page
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    page = client.get("/learn/python_basics_2/for_range/battle").get_data(as_text=True)
    assert "開発用：この問題を正解扱いにする" in page
