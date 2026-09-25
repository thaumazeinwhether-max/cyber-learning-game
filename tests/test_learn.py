from pathlib import Path

import pytest

from src.app import app
from src.learn_data import COURSES


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def page_text(response):
    return response.get_data(as_text=True)


def finish_lessons(client, course_id):
    course = COURSES[course_id]
    for lesson in course["lessons"]:
        lesson_id = lesson["id"]
        client.post(f"/learn/{course_id}/{lesson_id}/start")
        for index, question in enumerate(lesson["questions"]):
            answer = str(question["answer"]) if course_id == "it" else question["answer"]
            client.post(
                f"/learn/{course_id}/{lesson_id}/answer",
                data={"question_index": str(index), "answer": answer},
            )
            response = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return response


def finish_first_lesson(client, course_id):
    lesson = COURSES[course_id]["lessons"][0]
    lesson_id = lesson["id"]
    client.post(f"/learn/{course_id}/{lesson_id}/start")
    for index, question in enumerate(lesson["questions"]):
        answer = str(question["answer"]) if course_id == "it" else question["answer"]
        client.post(
            f"/learn/{course_id}/{lesson_id}/answer",
            data={"question_index": str(index), "answer": answer},
        )
        response = client.post(f"/learn/{course_id}/{lesson_id}/next")
    return response


def test_learn_home_and_courses(client):
    response = client.get("/learn/")
    assert response.status_code == 200
    assert "サイバー防衛学校" in page_text(response)
    assert "IT基礎訓練" in page_text(response)
    assert "Python基礎訓練" in page_text(response)
    assert "学習 → 戦闘" in page_text(response)


def test_it_lesson_and_locked_lesson(client):
    assert "コンピュータの基本" in page_text(client.get("/learn/it/computer/"))
    assert "これだけ覚えよう" in page_text(client.get("/learn/it/computer/"))
    response = client.get("/learn/it/network/")
    assert response.status_code == 302


@pytest.mark.parametrize("course_id", ["it", "python"])
def test_training_selection_shows_initial_statuses(client, course_id):
    response = client.get(f"/learn/{course_id}/")
    page = page_text(response)
    assert response.status_code == 200
    assert "訓練選択" in page
    assert "▶ 挑戦可能" in page
    assert "未開始" in page
    assert page.count("LOCKED / ロック中") == 3


@pytest.mark.parametrize("course_id", ["it", "python"])
def test_training_clear_waits_for_player_choice_and_unlocks_next(client, course_id):
    first_id = COURSES[course_id]["lessons"][0]["id"]
    second_id = COURSES[course_id]["lessons"][1]["id"]
    response = finish_first_lesson(client, course_id)
    assert response.status_code == 302
    assert response.location.endswith(f"/learn/{course_id}/{first_id}/complete")

    clear_page = page_text(client.get(response.location))
    assert "TRAINING COMPLETE" in clear_page
    assert "次の訓練へ" in clear_page
    assert f"/learn/{course_id}/{second_id}/" in clear_page
    assert "訓練選択へ戻る" in clear_page
    assert f"/learn/{course_id}/" in clear_page

    selection = page_text(client.get(f"/learn/{course_id}/"))
    assert "✓ 修了済み" in selection
    assert "▶ 挑戦可能" in selection
    assert "LOCKED / ロック中" in selection
    assert client.get(f"/learn/{course_id}/{second_id}/").status_code == 200


def test_last_training_clear_unlocks_boss_and_offers_choice(client):
    result = finish_lessons(client, "it")
    assert result.location.endswith("/learn/it/web/complete")
    clear_page = page_text(client.get("/learn/it/web/complete"))
    assert "TRAINING COMPLETE" in clear_page
    assert "ボス戦へ" in clear_page
    assert "訓練選択へ戻る" in clear_page
    selection = page_text(client.get("/learn/it/"))
    assert "ボス戦開始" in selection
    assert selection.count("✓ 修了済み") == 3
    start = client.post("/learn/it/boss/start")
    assert start.location.endswith("/learn/it/boss")


def test_it_battle_wrong_then_next_question(client):
    client.post("/learn/it/computer/start")
    wrong = client.post(
        "/learn/it/computer/answer",
        data={"question_index": "0", "answer": "1"}, follow_redirects=True,
    )
    assert "不正解" in page_text(wrong)
    assert "INCORRECT / ATTACK FAILED" in page_text(wrong)
    assert "ENEMY HP: 1 / 1" in page_text(wrong)
    assert "ENEMY DETECTED" in page_text(wrong)
    assert "回答する" not in page_text(wrong)

    repeat = client.post(
        "/learn/it/computer/answer",
        data={"question_index": "0", "answer": "0"}, follow_redirects=True,
    )
    assert "INCORRECT" in page_text(repeat)
    next_battle = client.post("/learn/it/computer/next", follow_redirects=True)
    assert "QUESTION 2 / 2" in page_text(next_battle)


def test_it_boss_wrong_attempt_then_perfect_retry(client):
    finish_lessons(client, "it")
    assert "ボス戦開始" in page_text(client.get("/learn/it/"))
    client.post("/learn/it/boss/start")
    assert "BOSS HP: ■■■" in page_text(client.get("/learn/it/boss"))
    assert 'role="progressbar"' in page_text(client.get("/learn/it/boss"))

    wrong = client.post(
        "/learn/it/boss/answer", data={"question_index": "0", "answer": "true"},
        follow_redirects=True,
    )
    assert "INCORRECT" in page_text(wrong)
    assert "BOSS HP: ■■■" in page_text(wrong)
    assert "× 間違っている" in page_text(wrong)
    assert "回答する" not in page_text(wrong)
    client.post("/learn/it/boss/next")
    client.post("/learn/it/boss/answer", data={"question_index": "1", "answer": "DNS"})
    client.post("/learn/it/boss/next")
    client.post("/learn/it/boss/answer", data={"question_index": "2", "answer": "true"})
    failed = client.post("/learn/it/boss/next", follow_redirects=True)
    assert "BOSS BATTLE FAILED" in page_text(failed)
    assert "2 / 3" in page_text(failed)
    assert client.get("/learn/it/complete").status_code == 302

    client.post("/learn/it/boss/start")
    first = client.post("/learn/it/boss/answer", data={"question_index": "0", "answer": "false"}, follow_redirects=True)
    assert "BOSS HP: ■■□" in page_text(first)
    client.post("/learn/it/boss/next")
    client.post("/learn/it/boss/answer", data={"question_index": "1", "answer": "DNS"})
    client.post("/learn/it/boss/next")
    client.post("/learn/it/boss/answer", data={"question_index": "2", "answer": "true"})
    complete = client.post("/learn/it/boss/next", follow_redirects=True)
    assert "IT基礎訓練 修了" in page_text(complete)
    assert "BOSS DEFEATED" in page_text(complete)
    assert "訓練選択へ戻る" in page_text(complete)
    assert "Learnトップへ戻る" in page_text(complete)


def test_python_lesson_and_code_battle(client):
    lesson_page = client.get("/learn/python/variables/")
    assert lesson_page.status_code == 200
    assert "<pre><code>" in page_text(lesson_page)
    assert "このコード" not in page_text(lesson_page) or "最初の行" in page_text(lesson_page)

    client.post("/learn/python/variables/start")
    wrong = client.post(
        "/learn/python/variables/answer",
        data={"question_index": "0", "answer": "x = 11"}, follow_redirects=True,
    )
    assert "不正解" in page_text(wrong)
    assert "ENEMY HP: 1 / 1" in page_text(wrong)
    assert "x = 10" in page_text(wrong)
    assert "回答する" not in page_text(wrong)


def test_python_quote_styles_and_no_execution(client):
    client.post("/learn/python/variables/start")
    client.post("/learn/python/variables/answer", data={"question_index": "0", "answer": "x = 10"})
    client.post("/learn/python/variables/next")
    same_meaning = client.post(
        "/learn/python/variables/answer",
        data={"question_index": "1", "answer": 'print("Hello")'}, follow_redirects=True,
    )
    assert "敵を撃破" in page_text(same_meaning)

    client.post("/learn/python/variables/next")
    client.post("/learn/python/conditions/start")
    marker = Path(__file__).with_name("should_not_exist.txt")
    assert not marker.exists()
    malicious_code = f"__import__('pathlib').Path({str(marker)!r}).touch()"
    response = client.post(
        "/learn/python/conditions/answer",
        data={"question_index": "0", "answer": malicious_code}, follow_redirects=True,
    )
    assert "不正解" in page_text(response)
    assert not marker.exists()


def test_python_boss_debugging_requires_perfect_retry(client):
    finish_lessons(client, "python")
    client.post("/learn/python/boss/start")
    wrong = client.post(
        "/learn/python/boss/answer",
        data={"question_index": "0", "answer": "incorrect", "corrected_code": "age = 20"},
        follow_redirects=True,
    )
    assert "INCORRECT" in page_text(wrong)
    assert "if age &gt;= 18:" in page_text(wrong)
    client.post("/learn/python/boss/next")
    client.post("/learn/python/boss/answer", data={"question_index": "1", "answer": "correct"})
    client.post("/learn/python/boss/next")
    client.post(
        "/learn/python/boss/answer",
        data={"question_index": "2", "answer": "incorrect", "corrected_code": 'print("Hello")'},
    )
    failed = client.post("/learn/python/boss/next", follow_redirects=True)
    assert "BOSS BATTLE FAILED" in page_text(failed)

    client.post("/learn/python/boss/start")
    first = client.post(
        "/learn/python/boss/answer",
        data={"question_index": "0", "answer": "incorrect", "corrected_code": 'age = 20\nif age >= 18:\n    print("adult")'},
        follow_redirects=True,
    )
    assert "BOSS HP: ■■□" in page_text(first)
    client.post("/learn/python/boss/next")
    client.post("/learn/python/boss/answer", data={"question_index": "1", "answer": "correct"})
    client.post("/learn/python/boss/next")
    client.post(
        "/learn/python/boss/answer",
        data={"question_index": "2", "answer": "incorrect", "corrected_code": 'print("Hello")'},
    )
    complete = client.post("/learn/python/boss/next", follow_redirects=True)
    assert "Python基礎訓練 修了" in page_text(complete)


def test_dev_shortcut_disabled_by_default_and_zero(client, monkeypatch):
    client.post("/learn/it/computer/start")
    page = page_text(client.get("/learn/it/computer/battle"))
    assert "DEV MODE" not in page
    assert "開発用：この問題を正解扱いにする" not in page
    forged = client.post(
        "/learn/it/computer/answer",
        data={"question_index": "0", "action": "dev_skip"}, follow_redirects=True,
    )
    assert "ENEMY HP: 1 / 1" in page_text(forged)
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "0")
    assert "DEV MODE" not in page_text(client.get("/learn/it/computer/battle"))


def test_dev_shortcut_uses_normal_progress(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    client.post("/learn/it/computer/start")
    page = page_text(client.get("/learn/it/computer/battle"))
    assert "DEV MODE" in page
    assert "開発用：この問題を正解扱いにする" in page
    skipped = client.post(
        "/learn/it/computer/answer",
        data={"question_index": "0", "action": "dev_skip"}, follow_redirects=True,
    )
    assert "敵を撃破" in page_text(skipped)
    client.post("/learn/it/computer/next")
    skipped_again = client.post(
        "/learn/it/computer/answer",
        data={"question_index": "1", "action": "dev_skip"}, follow_redirects=True,
    )
    assert "敵を撃破" in page_text(skipped_again)
    next_lesson = client.post("/learn/it/computer/next", follow_redirects=True)
    assert "TRAINING COMPLETE" in page_text(next_lesson)
    assert "次の訓練へ" in page_text(next_lesson)
    selection = page_text(client.get("/learn/it/"))
    assert "✓ 修了済み" in selection
    assert "▶ 挑戦可能" in selection


def test_dev_shortcut_reduces_boss_hp(client, monkeypatch):
    finish_lessons(client, "it")
    client.post("/learn/it/boss/start")
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    first = client.post(
        "/learn/it/boss/answer",
        data={"question_index": "0", "action": "dev_skip"}, follow_redirects=True,
    )
    assert "BOSS HP: ■■□" in page_text(first)
    assert "DEV MODE" in page_text(first)
