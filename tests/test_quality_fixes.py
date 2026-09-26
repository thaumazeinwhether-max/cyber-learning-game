"""総監査で見つかった採点・選択肢・進捗の回帰テスト。"""

import copy
import importlib
import shutil
import uuid
from pathlib import Path

import pytest

from src.answer_check import is_correct
from src.app import create_app
from src.choice_order import arrange_choices
from src.learn_data import COURSES
from src.learn_routes import FORMAL_COURSE_IDS


@pytest.fixture
def local_temp_path():
    """作業領域内を使い、OSの一時領域の権限に依存しない。"""
    path = Path(__file__).parents[1] / ".pytest_cache" / f"quality_{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    yield path
    # Windows/OneDriveでディレクトリの解放が遅れる場合がある。キャッシュ領域なので残存しても無害。
    shutil.rmtree(path, ignore_errors=True)


def question(course_id, lesson_id, index):
    lesson = next(item for item in COURSES[course_id]["lessons"] if item["id"] == lesson_id)
    return lesson["questions"][index]


def test_python_accepted_alternatives_and_wrong_code(local_temp_path):
    add = question("python_basics_2", "arguments", 0)
    double = question("python_basics_2", "arguments", 3)
    count = question("python_basics_2", "while", 0)
    greeting = question("python_basics_1", "print", 0)
    assert is_correct("python_basics_2", add, "def add(a, b):\n    return b + a")
    assert is_correct("python_basics_2", double, "def double(number):\n    return number + number")
    assert is_correct("python_basics_2", count, "count = 0\nwhile count < 3:\n    print(count)\n    count += 1")
    assert is_correct("python_basics_1", greeting, "print('Hello')")
    assert not is_correct("python_basics_2", add, "def add(a, b):\n    return a - b")
    assert not is_correct("python_basics_2", double, "def double(number):\n    return number + 2")
    route = question("flask_basics", "route", 0)
    assert is_correct("flask_basics", route, "@app.get('/')\ndef index():\n    return 'Hello'")
    assert not is_correct("flask_basics", route, "@app.get('/wrong')\ndef index():\n    return 'Hello'")
    post_review = next(item for item in COURSES["flask_basics"]["boss"] if "POSTだけ" in item["prompt"])
    assert is_correct("flask_basics", post_review, "incorrect", "@app.post('/answer')\ndef answer():\n    return 'ok'")
    # 送られたPythonはAST解析のみ。ファイル操作を含む入力でも実行しない。
    marker = local_temp_path / "must_not_exist"
    unsafe = f"open({str(marker)!r}, 'w').write('x')"
    assert not is_correct("python_basics_2", add, unsafe)
    assert not marker.exists()


def test_python_questions_have_clear_names_and_boss_precondition():
    course = COURSES["python_basics_2"]
    assert "third_score" in question("python_basics_2", "list", 3)["prompt"]
    assert "second_last" not in question("python_basics_2", "list", 3)["answer"]
    for item in course["lessons"][0]["questions"]:
        assert "i" in item["prompt"]
    random_question = next(item for item in course["boss"] if "random.randint(1, 3)" in item["prompt"])
    assert "事前のimportはありません" in random_question["prompt"]
    assert not random_question["valid"]


COURSE_MODULES = {
    "network_basics": "network_basics_data",
    "web_http": "web_http_data",
    "web_creation": "web_creation_data",
    "flask_basics": "flask_basics_data",
    "database_sql": "database_sql_data",
    "git_dev": "git_dev_data",
    "security_basics": "security_basics_data",
    "web_security": "web_security_data",
    "incident_response": "incident_response_data",
}


@pytest.mark.parametrize("course_id", COURSE_MODULES)
def test_choice_order_is_stable_and_has_no_old_cycle(course_id):
    course = COURSES[course_id]
    selections = [item for lesson in course["lessons"] for item in lesson["questions"] if "options" in item]
    actual_positions = [item["answer"] for item in selections]
    old_positions = [
        (-(lesson_number + question_number)) % 4
        for lesson_number, lesson in enumerate(course["lessons"])
        for question_number, item in enumerate(lesson["questions"])
        if "options" in item
    ]
    assert len(actual_positions) == len(old_positions)
    assert sum(a != b for a, b in zip(actual_positions, old_positions)) >= 4
    assert len(set(actual_positions)) == 4
    boss_positions = [item["answer"] for item in course["boss"] if "options" in item]
    boss_old_positions = [(-index) % 4 for index, item in enumerate(course["boss"]) if "options" in item]
    assert any(a != b for a, b in zip(boss_positions, boss_old_positions))
    for item in selections:
        assert is_correct(course_id, item, str(item["answer"]))
        assert not is_correct(course_id, item, str((item["answer"] + 1) % 4))

    module = importlib.reload(importlib.import_module("src." + COURSE_MODULES[course_id]))
    reloaded = next(value for name, value in vars(module).items() if name.endswith("_COURSE"))
    again = [item["answer"] for lesson in reloaded["lessons"] for item in lesson["questions"] if "options" in item]
    assert again == actual_positions
    assert [item["answer"] for item in reloaded["boss"] if "options" in item] == boss_positions


def test_choice_helper_maps_correct_answer_after_shuffle():
    course = {"curriculum_number": 99, "lessons": [{"id": "unit", "questions": [
        {"prompt": "例題", "options": ["誤1", "正", "誤2", "誤3"], "answer": 1}
    ]}], "boss": []}
    other = copy.deepcopy(course)
    arrange_choices(course)
    arrange_choices(other)
    assert course == other
    item = course["lessons"][0]["questions"][0]
    assert item["options"][item["answer"]] == "正"


def test_secret_key_and_progress_survive_app_recreation(local_temp_path, monkeypatch):
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)
    first_app = create_app(local_temp_path)
    first_app.config["TESTING"] = True
    first_client = first_app.test_client()
    with first_client.session_transaction() as saved:
        saved.permanent = True
        saved["learn_progress"] = {"computer_os": {"completed_lessons": ["hardware"]}}
    first_client.get("/learn/")
    cookie = first_client.get_cookie(first_app.config["SESSION_COOKIE_NAME"])
    assert cookie is not None
    assert "Expires=" in first_client.get("/learn/").headers["Set-Cookie"]

    second_app = create_app(local_temp_path)
    second_app.config["TESTING"] = True
    assert first_app.secret_key == second_app.secret_key
    second_client = second_app.test_client()
    second_client.set_cookie(cookie.key, cookie.value)
    with second_client.session_transaction() as loaded:
        assert loaded["learn_progress"]["computer_os"]["completed_lessons"] == ["hardware"]
    assert second_client.get("/learn/computer_os/").status_code == 200
    key_file = local_temp_path / "learn_secret_key"
    assert key_file.exists() and key_file.read_text().strip() == first_app.secret_key
    assert "instance/" in (Path(__file__).parents[1] / ".gitignore").read_text(encoding="utf-8")


def test_environment_secret_takes_priority(local_temp_path, monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-key-for-this-isolated-test")
    app = create_app(local_temp_path)
    assert app.secret_key == "test-key-for-this-isolated-test"
    assert not (local_temp_path / "learn_secret_key").exists()


def test_safe_database_examples_and_boss_scenarios():
    for course_id, lesson_id in (("database_sql", "web_db"), ("web_security", "safe_db")):
        lesson = next(item for item in COURSES[course_id]["lessons"] if item["id"] == lesson_id)
        blocks = [block for section in lesson["sections"] for block in section["blocks"]]
        assert any("cursor.execute" in str(block) and "(user_id,)" in str(block) for block in blocks)
        assert any("SQL" in str(block) and "分" in str(block) for block in blocks)
    scenarios = {
        "database_sql": "フォーム",
        "git_dev": "個人設定",
        "security_basics": "機密な進捗",
        "web_security": "Session",
        "incident_response": "500",
    }
    for course_id, phrase in scenarios.items():
        assert any(phrase in item["prompt"] for item in COURSES[course_id]["boss"])
    assert all("unit_id" in item for item in COURSES["incident_response"]["boss"])
    assert {item["unit_id"] for item in COURSES["incident_response"]["boss"]} <= {
        lesson["id"] for lesson in COURSES["incident_response"]["lessons"]
    }


def test_dev_shortcut_finishes_all_twelve_courses_in_order(local_temp_path, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    application = create_app(local_temp_path)
    application.config["TESTING"] = True
    client = application.test_client()
    for course_id in FORMAL_COURSE_IDS:
        course = COURSES[course_id]
        assert client.get(f"/learn/{course_id}/").status_code == 200
        for lesson in course["lessons"]:
            lesson_id = lesson["id"]
            assert client.post(f"/learn/{course_id}/{lesson_id}/start").status_code == 302
            for index, _ in enumerate(lesson["questions"]):
                assert client.post(
                    f"/learn/{course_id}/{lesson_id}/answer",
                    data={"question_index": str(index), "action": "dev_skip"},
                ).status_code == 302
                result = client.post(f"/learn/{course_id}/{lesson_id}/next")
            assert result.location.endswith(f"/learn/{course_id}/{lesson_id}/complete")
        assert client.post(f"/learn/{course_id}/boss/start").status_code == 302
        for index, _ in enumerate(course["boss"]):
            assert client.post(
                f"/learn/{course_id}/boss/answer",
                data={"question_index": str(index), "action": "dev_skip"},
            ).status_code == 302
            result = client.post(f"/learn/{course_id}/boss/next")
        assert result.location.endswith(f"/learn/{course_id}/complete")
        with client.session_transaction() as saved:
            assert saved["learn_progress"][course_id]["course_complete"]
    assert "LEARN PHASE COMPLETE" in client.get("/learn/").get_data(as_text=True)
