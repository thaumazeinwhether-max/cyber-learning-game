"""正式第2〜4訓練の教材、採点、解放順と完走を確認する。"""

import pytest

from src.answer_check import is_correct
from src.app import app
from src.learn_data import COURSES


FORMAL_IDS = ("computer_os", "python_basics_1", "network_basics", "web_http")
NEW_IDS = FORMAL_IDS[1:]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def unlock_previous(client, course_id):
    index = FORMAL_IDS.index(course_id)
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {
            prior_id: {"course_complete": True}
            for prior_id in FORMAL_IDS[:index]
        }


def answer_for(course_id, question):
    if question.get("mode", COURSES[course_id]["question_mode"]) == "code":
        return question["answer"]
    return str(question["answer"])


def finish_unit(client, course_id, lesson, shortcut=False):
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    for index, question in enumerate(lesson["questions"]):
        data = {"question_index": str(index)}
        if shortcut:
            data["action"] = "dev_skip"
        else:
            data["answer"] = answer_for(course_id, question)
        client.post(f"/learn/{course_id}/{lesson_id}/answer", data=data)
        result = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return result


def finish_course(client, course_id, shortcut=False):
    course = COURSES[course_id]
    for lesson in course["lessons"]:
        finish_unit(client, course_id, lesson, shortcut)
    client.post(f"/learn/{course_id}/boss/start")
    for index, question in enumerate(course["boss"]):
        data = {"question_index": str(index)}
        if shortcut:
            data["action"] = "dev_skip"
        elif course["question_mode"] == "code":
            data["answer"] = "correct" if question["valid"] else "incorrect"
            if not question["valid"]:
                data["corrected_code"] = question["answer"]
        else:
            data["answer"] = str(question["answer"])
        client.post(f"/learn/{course_id}/boss/answer", data=data)
        result = client.post(f"/learn/{course_id}/boss/next")
    return result


def test_formal_course_order_and_locked_routes(client):
    home = client.get("/learn/").get_data(as_text=True)
    for number, course_id in enumerate(FORMAL_IDS, start=1):
        assert f"正式カリキュラム 第{number}訓練" in home
        assert COURSES[course_id]["title"] in home
    assert client.get("/learn/computer_os/").status_code == 200
    for course_id in NEW_IDS:
        assert client.get(f"/learn/{course_id}/").status_code == 403
        assert client.post(f"/learn/{course_id}/boss/start").status_code == 403


@pytest.mark.parametrize("course_id,units,boss_count", [
    ("python_basics_1", 10, 12),
    ("network_basics", 10, 14),
    ("web_http", 10, 14),
])
def test_curriculum_structure_and_textbook_blocks(course_id, units, boss_count):
    course = COURSES[course_id]
    assert len(course["lessons"]) == units
    assert len(course["boss"]) == boss_count
    for lesson in course["lessons"]:
        assert len(lesson["questions"]) == 4
        assert lesson["objective"] and lesson["why"] and lesson["connection"]
        assert len(lesson["sections"]) >= 3
        blocks = [block for section in lesson["sections"] for block in section["blocks"]]
        block_types = {block["type"] for block in blocks}
        assert {"paragraph", "key_points"} <= block_types
        assert "table" in block_types or "code" in block_types
        assert all(question["explanation"] for question in lesson["questions"])
        for question in lesson["questions"]:
            if question.get("mode", course["question_mode"]) == "choice":
                assert len(question["options"]) == 4
            assert is_correct(course_id, question, answer_for(course_id, question))


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_every_unit_page_and_full_unlock_flow(client, course_id):
    unlock_previous(client, course_id)
    course = COURSES[course_id]
    assert client.get(f"/learn/{course_id}/").status_code == 200
    second_id = course["lessons"][1]["id"]
    assert client.get(f"/learn/{course_id}/{second_id}/").status_code == 302
    for lesson in course["lessons"]:
        lesson_id = lesson["id"]
        page = client.get(f"/learn/{course_id}/{lesson_id}/")
        assert page.status_code == 200
        text = page.get_data(as_text=True)
        assert "学習目標" in text
        assert "前のUNITとの接続" in text
        assert "これだけ覚えよう" in text
        assert 'class="chapter-section"' in text
        assert "訓練開始" in text
        result = finish_unit(client, course_id, lesson)
        assert result.location.endswith(f"/learn/{course_id}/{lesson_id}/complete")
    selection = client.get(f"/learn/{course_id}/").get_data(as_text=True)
    assert "▶ 挑戦可能" in selection
    assert client.post(f"/learn/{course_id}/boss/start").location.endswith(
        f"/learn/{course_id}/boss"
    )


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_wrong_answer_requires_full_retry(client, course_id):
    unlock_previous(client, course_id)
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    for index, question in enumerate(lesson["questions"]):
        wrong = "not valid code" if course_id == "python_basics_1" else str((question["answer"] + 1) % 4)
        answer = wrong if index == 0 else answer_for(course_id, question)
        client.post(f"/learn/{course_id}/{lesson_id}/answer",
                    data={"question_index": str(index), "answer": answer})
        client.post(f"/learn/{course_id}/{lesson_id}/next")
    page = client.get(f"/learn/{course_id}/{lesson_id}/result").get_data(as_text=True)
    assert "UNIT CLEAR FAILED" in page
    assert "3 / 4" in page
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert lesson_id not in progress["completed_lessons"]
        assert progress["correct_count"] == 3
    assert client.get(f"/learn/{course_id}/{COURSES[course_id]['lessons'][1]['id']}/").status_code == 302
    result = finish_unit(client, course_id, lesson)
    assert result.location.endswith(f"/learn/{course_id}/{lesson_id}/complete")


def test_python_ast_equivalent_code_and_no_execution():
    question = COURSES["python_basics_1"]["lessons"][1]["questions"][0]
    assert is_correct("python_basics_1", question, "print('Hello')")
    assert not is_correct("python_basics_1", question, "print('Wrong')")
    assert not is_correct("python_basics_1", question, "print('Hello'); open('x','w')")
    arithmetic = COURSES["python_basics_1"]["lessons"][4]["questions"][0]
    assert is_correct("python_basics_1", arithmetic, "total = 2 + 3")
    assert not is_correct("python_basics_1", arithmetic, "total = 2 * 3")
    reassignment = COURSES["python_basics_1"]["lessons"][2]["questions"][3]
    assert is_correct("python_basics_1", reassignment, "score += 10")
    boss = COURSES["python_basics_1"]["boss"][1]
    assert is_correct("python_basics_1", boss, "incorrect", "print('Hello')")
    assert not is_correct("python_basics_1", boss, "incorrect", "print('Wrong')")


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_answer_feedback_and_duplicate_post(client, course_id):
    unlock_previous(client, course_id)
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    question = lesson["questions"][0]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    answer = answer_for(course_id, question)
    response = client.post(
        f"/learn/{course_id}/{lesson_id}/answer",
        data={"question_index": "0", "answer": answer},
        follow_redirects=True,
    )
    page = response.get_data(as_text=True)
    assert "CORRECT / HIT" in page
    assert question["explanation"] in page
    assert "次の問題へ" in page
    assert "<form method=\"post\" action=\"/learn/" + course_id + "/" + lesson_id + "/answer\"" not in page
    client.post(f"/learn/{course_id}/{lesson_id}/answer",
                data={"question_index": "0", "answer": answer})
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][course_id]
        assert progress["correct_count"] == 1
    client.post(f"/learn/{course_id}/{lesson_id}/next")
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][course_id]["question_index"] == 1


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_normal_answers_complete_boss_and_unlock_next(client, course_id):
    unlock_previous(client, course_id)
    result = finish_course(client, course_id)
    assert result.location.endswith(f"/learn/{course_id}/complete")
    complete = client.get(result.location)
    assert complete.status_code == 200
    assert COURSES[course_id]["title"] in complete.get_data(as_text=True)
    index = FORMAL_IDS.index(course_id)
    if index + 1 < len(FORMAL_IDS):
        assert client.get(f"/learn/{FORMAL_IDS[index + 1]}/").status_code == 200


@pytest.mark.parametrize("course_id", NEW_IDS)
def test_boss_wrong_answer_does_not_complete(client, course_id):
    unlock_previous(client, course_id)
    for lesson in COURSES[course_id]["lessons"]:
        finish_unit(client, course_id, lesson)
    course = COURSES[course_id]
    client.post(f"/learn/{course_id}/boss/start")
    first = course["boss"][0]
    if course["question_mode"] == "code":
        wrong = "incorrect" if first["valid"] else "correct"
    elif first["type"] == "true_false":
        wrong = "false" if first["answer"] == "true" else "true"
    else:
        wrong = "wrong"
    client.post(f"/learn/{course_id}/boss/answer",
                data={"question_index": "0", "answer": wrong})
    client.post(f"/learn/{course_id}/boss/next")
    for index, question in enumerate(course["boss"][1:], start=1):
        data = {"question_index": str(index)}
        if course["question_mode"] == "code":
            data["answer"] = "correct" if question["valid"] else "incorrect"
            if not question["valid"]:
                data["corrected_code"] = question["answer"]
        else:
            data["answer"] = str(question["answer"])
        client.post(f"/learn/{course_id}/boss/answer", data=data)
        result = client.post(f"/learn/{course_id}/boss/next")
    assert result.location.endswith(f"/learn/{course_id}/boss/result")
    with client.session_transaction() as browser_session:
        assert not browser_session["learn_progress"][course_id]["course_complete"]


def test_dev_can_complete_all_four_courses_in_order(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    for course_id in FORMAL_IDS:
        result = finish_course(client, course_id, shortcut=True)
        assert result.location.endswith(f"/learn/{course_id}/complete")
        complete = client.get(result.location).get_data(as_text=True)
        assert "COURSE COMPLETE" in complete or "COMPUTER & OS TRAINING COMPLETE" in complete
        with client.session_transaction() as browser_session:
            assert browser_session["learn_progress"][course_id]["course_complete"]
    final_page = client.get("/learn/web_http/complete").get_data(as_text=True)
    assert "Python基礎Ⅱ" in final_page
    assert "準備中" in final_page
    assert client.get("/learn/network_basics/").status_code == 200


def test_dev_button_hidden_by_default_and_html_escaped(client, monkeypatch):
    unlock_previous(client, "python_basics_1")
    client.post("/learn/python_basics_1/program/start")
    page = client.get("/learn/python_basics_1/program/battle").get_data(as_text=True)
    assert "開発用：この問題を正解扱いにする" not in page
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    page = client.get("/learn/python_basics_1/program/battle").get_data(as_text=True)
    assert "開発用：この問題を正解扱いにする" in page
    unlock_previous(client, "web_http")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"]
        progress["web_http"] = {
            "completed_lessons": [lesson["id"] for lesson in COURSES["web_http"]["lessons"][:4]]
        }
        browser_session["learn_progress"] = progress
    page = client.get("/learn/web_http/response/").get_data(as_text=True)
    assert "&lt;h1&gt;" in page
    assert "<h1>学習を始めよう</h1>" not in page


def test_legacy_courses_remain_available(client):
    assert client.get("/learn/it/").status_code == 200
    assert client.get("/learn/python/").status_code == 200


def test_existing_session_with_missing_fields_remains_readable(client):
    with client.session_transaction() as browser_session:
        browser_session["learn_progress"] = {"computer_os": {"course_complete": True}}
    assert client.get("/learn/computer_os/").status_code == 200
    assert client.get("/learn/computer_os/hardware/").status_code == 200
