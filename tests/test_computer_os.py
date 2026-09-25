import pytest

from src.app import app
from src.answer_check import is_correct
from src.learn_data import COURSES


COURSE_ID = "computer_os"
COURSE = COURSES[COURSE_ID]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("LEARN_DEV_SHORTCUT", raising=False)
    app.config["TESTING"] = True
    return app.test_client()


def page_text(response):
    return response.get_data(as_text=True)


def finish_unit(client, lesson, use_shortcut=False):
    lesson_id = lesson["id"]
    client.post(f"/learn/{COURSE_ID}/{lesson_id}/start")
    for index, question in enumerate(lesson["questions"]):
        answer = {"question_index": str(index)}
        if use_shortcut:
            answer["action"] = "dev_skip"
        else:
            answer["answer"] = str(question["answer"])
        client.post(f"/learn/{COURSE_ID}/{lesson_id}/answer", data=answer)
        result = client.post(f"/learn/{COURSE_ID}/{lesson_id}/next")
    return result


def finish_all_units(client, use_shortcut=False):
    for lesson in COURSE["lessons"]:
        finish_unit(client, lesson, use_shortcut)


def test_first_training_has_six_units_and_fourteen_boss_questions(client):
    selection = client.get(f"/learn/{COURSE_ID}/")
    assert selection.status_code == 200
    assert "コンピュータ・OS基礎訓練" in page_text(selection)
    assert page_text(selection).count("LOCKED / ロック中") == 6
    assert len(COURSE["lessons"]) == 6
    assert len(COURSE["boss"]) == 14
    assert all(4 <= len(lesson["questions"]) <= 6 for lesson in COURSE["lessons"])
    assert all(len(question["options"]) == 4 for lesson in COURSE["lessons"] for question in lesson["questions"])
    assert {question["type"] for question in COURSE["boss"]} == {"true_false", "term", "application"}
    assert client.get(f"/learn/{COURSE_ID}/os/").status_code == 302
    assert client.post(f"/learn/{COURSE_ID}/boss/start").location.endswith(f"/learn/{COURSE_ID}/")


def test_term_question_accepts_only_listed_alternative_answers():
    question = {"type": "term", "answer": "RAM", "accepted_answers": ["RAM", "メモリ"]}
    assert is_correct(COURSE_ID, question, " ram ")
    assert is_correct(COURSE_ID, question, "メモリ")
    assert not is_correct(COURSE_ID, question, "SSD")


@pytest.mark.parametrize(
    ("lesson_id", "required_text"),
    [
        ("hardware", "一般的なRAMは揮発性"),
        ("os", "Linuxはプログラミング言語ではありません"),
        ("files", "photo.jpgをphoto.txtへ改名しても"),
        ("paths", "src\\app.py"),
        ("processes", "実行中のプログラムに関係する活動単位"),
        ("interfaces", "PowerShellはWindowsなどで利用できるコマンドラインシェル"),
    ],
)
def test_unit_lessons_show_required_concepts(client, lesson_id, required_text):
    lesson_ids = [lesson["id"] for lesson in COURSE["lessons"]]
    for prior_id in lesson_ids[:lesson_ids.index(lesson_id)]:
        prior_lesson = next(lesson for lesson in COURSE["lessons"] if lesson["id"] == prior_id)
        finish_unit(client, prior_lesson)
    response = client.get(f"/learn/{COURSE_ID}/{lesson_id}/")
    assert response.status_code == 200
    page = page_text(response)
    assert "学習目標" in page
    assert "なぜ学ぶのか" in page
    assert "前のUNITとの接続" in page
    assert "このUNITの内容" in page
    assert "よくある勘違い" in page
    assert "これだけ覚えよう" in page
    assert page.count('class="chapter-section"') == 4
    assert 'class="comparison-table"' in page
    assert required_text in page


def test_chapter_blocks_have_textbook_structure():
    for lesson in COURSE["lessons"]:
        assert len(lesson["sections"]) >= 4
        assert lesson["objective"] and lesson["why"] and lesson["connection"]
        blocks = [block for section in lesson["sections"] for block in section["blocks"]]
        types = {block["type"] for block in blocks}
        assert {"paragraph", "table", "note", "warning", "key_points"} <= types
        key_points = [block for block in blocks if block["type"] == "key_points"]
        assert len(key_points) == 1
        assert 5 <= len(key_points[0]["items"]) <= 8
        for block in blocks:
            if block["type"] == "table":
                assert all(len(row) == len(block["columns"]) for row in block["rows"])


def test_chapter_code_flow_and_html_escaping(client, monkeypatch):
    blocks = COURSE["lessons"][0]["sections"][0]["blocks"]
    monkeypatch.setitem(blocks[0], "text", "安全な表示 <script>alert(1)</script> & 確認")
    hardware = page_text(client.get(f"/learn/{COURSE_ID}/hardware/"))
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in hardware
    assert "<script>alert(1)</script>" not in hardware
    assert "&amp; 確認" in hardware
    assert 'class="concept-flow chapter-flow"' in hardware

    finish_unit(client, COURSE["lessons"][0])
    finish_unit(client, COURSE["lessons"][1])
    files = page_text(client.get(f"/learn/{COURSE_ID}/files/"))
    assert '<figure class="chapter-code"><pre><code>' in files
    assert "cyber-learning-game" in files
    assert "README.md" in files


def test_unit_battle_wrong_shows_answer_and_cannot_retry_same_question(client):
    client.post(f"/learn/{COURSE_ID}/hardware/start")
    wrong = client.post(
        f"/learn/{COURSE_ID}/hardware/answer",
        data={"question_index": "0", "answer": "1"}, follow_redirects=True,
    )
    assert "ATTACK FAILED" in page_text(wrong)
    assert "ENEMY HP: 1 / 1" in page_text(wrong)
    assert COURSE["lessons"][0]["questions"][0]["wrong_explanations"]["1"] in page_text(wrong)
    assert COURSE["lessons"][0]["questions"][0]["explanation"] in page_text(wrong)
    assert "あなたの回答" in page_text(wrong)
    assert "正解：" in page_text(wrong)
    assert "回答する" not in page_text(wrong)
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][COURSE_ID]["correct_count"] == 0

    repeat = client.post(
        f"/learn/{COURSE_ID}/hardware/answer",
        data={"question_index": "0", "answer": "0"}, follow_redirects=True,
    )
    assert "INCORRECT" in page_text(repeat)
    assert "ENEMY HP: 1 / 1" in page_text(repeat)
    next_page = client.post(f"/learn/{COURSE_ID}/hardware/next", follow_redirects=True)
    assert "QUESTION 2 / 6" in page_text(next_page)
    for index, question in enumerate(COURSE["lessons"][0]["questions"][1:], start=1):
        client.post(
            f"/learn/{COURSE_ID}/hardware/answer",
            data={"question_index": str(index), "answer": str(question["answer"])},
        )
        result = client.post(f"/learn/{COURSE_ID}/hardware/next")
    assert result.location.endswith(f"/learn/{COURSE_ID}/hardware/result")
    result_page = page_text(client.get(result.location))
    assert "UNIT CLEAR FAILED" in result_page
    assert "5 / 6" in result_page
    assert "もう一度挑戦" in result_page
    assert "教材を読み直す" in result_page
    assert client.get(f"/learn/{COURSE_ID}/os/").status_code == 302


def test_correct_answer_shows_explanation_and_scores_once(client):
    client.post(f"/learn/{COURSE_ID}/hardware/start")
    first = client.post(
        f"/learn/{COURSE_ID}/hardware/answer",
        data={"question_index": "0", "answer": "0"}, follow_redirects=True,
    )
    page = page_text(first)
    assert "CORRECT / HIT" in page
    assert "ENEMY DEFEATED" in page
    assert "CPUが命令を実行" in page
    assert "今回の正解数：1 / 6" in page
    assert "次の問題へ" in page
    assert "回答する" not in page
    client.post(f"/learn/{COURSE_ID}/hardware/answer", data={"question_index": "0", "answer": "0"})
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][COURSE_ID]["correct_count"] == 1
    next_page = client.post(f"/learn/{COURSE_ID}/hardware/next", follow_redirects=True)
    assert "QUESTION 2 / 6" in page_text(next_page)
    client.post(f"/learn/{COURSE_ID}/hardware/answer", data={"question_index": "0", "answer": "0"})
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][COURSE_ID]["correct_count"] == 1


def test_failed_attempt_retry_resets_score_and_perfect_unlocks_next(client):
    lesson = COURSE["lessons"][0]
    client.post(f"/learn/{COURSE_ID}/hardware/start")
    for index, question in enumerate(lesson["questions"]):
        answer = "1" if index == 0 else str(question["answer"])
        client.post(
            f"/learn/{COURSE_ID}/hardware/answer",
            data={"question_index": str(index), "answer": answer},
        )
        result = client.post(f"/learn/{COURSE_ID}/hardware/next")
    assert result.location.endswith("/hardware/result")
    failed = page_text(client.get(result.location))
    assert "5 / 6" in failed
    assert "UNIT CLEAR FAILED" in failed
    assert f"/learn/{COURSE_ID}/hardware/" in failed
    assert client.get(f"/learn/{COURSE_ID}/os/").status_code == 302
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["attempt_result"]["correct_count"] == 5
        assert "hardware" not in progress["completed_lessons"]

    retry = client.post(f"/learn/{COURSE_ID}/hardware/start", follow_redirects=True)
    assert "QUESTION 1 / 6" in page_text(retry)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["correct_count"] == 0
        assert progress["attempt_result"] is None

    for index, question in enumerate(lesson["questions"]):
        client.post(
            f"/learn/{COURSE_ID}/hardware/answer",
            data={"question_index": str(index), "answer": str(question["answer"])},
        )
        result = client.post(f"/learn/{COURSE_ID}/hardware/next")
    assert result.location.endswith("/hardware/complete")
    perfect = page_text(client.get(result.location))
    assert "PERFECT" in perfect
    assert "6 / 6" in perfect
    assert "UNIT COMPLETE" in perfect
    assert client.get(f"/learn/{COURSE_ID}/os/").status_code == 200


def test_boss_stays_locked_until_every_unit_has_perfect_score(client):
    for lesson in COURSE["lessons"][:-1]:
        finish_unit(client, lesson)
    last_lesson = COURSE["lessons"][-1]
    client.post(f"/learn/{COURSE_ID}/{last_lesson['id']}/start")
    for index, question in enumerate(last_lesson["questions"]):
        answer = str(question["answer"])
        if index == 0:
            answer = str((question["answer"] + 1) % 4)
        client.post(
            f"/learn/{COURSE_ID}/{last_lesson['id']}/answer",
            data={"question_index": str(index), "answer": answer},
        )
        client.post(f"/learn/{COURSE_ID}/{last_lesson['id']}/next")
    assert "LOCKED / ロック中" in page_text(client.get(f"/learn/{COURSE_ID}/"))
    assert client.post(f"/learn/{COURSE_ID}/boss/start").location.endswith(f"/learn/{COURSE_ID}/")
    finish_unit(client, last_lesson)
    assert client.post(f"/learn/{COURSE_ID}/boss/start").location.endswith(f"/learn/{COURSE_ID}/boss")


def test_all_six_units_unlock_boss_and_session_tracks_progress(client):
    for number, lesson in enumerate(COURSE["lessons"]):
        result = finish_unit(client, lesson)
        assert result.location.endswith(f"/{lesson['id']}/complete")
        if number + 1 < len(COURSE["lessons"]):
            next_id = COURSE["lessons"][number + 1]["id"]
            assert client.get(f"/learn/{COURSE_ID}/{next_id}/").status_code == 200

    selection = page_text(client.get(f"/learn/{COURSE_ID}/"))
    assert selection.count("✓ 修了済み") == 6
    assert "SYSTEM CORE" in selection
    assert "HP14" in selection
    assert "ボス戦開始" in selection
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert len(progress["completed_lessons"]) == 6
        assert progress["course_complete"] is False


def test_boss_true_false_term_application_and_completion(client):
    finish_all_units(client)
    client.post(f"/learn/{COURSE_ID}/boss/start")
    first_page = page_text(client.get(f"/learn/{COURSE_ID}/boss"))
    assert "SYSTEM CORE" in first_page
    assert 'aria-valuenow="14"' in first_page

    first_hit = client.post(
        f"/learn/{COURSE_ID}/boss/answer",
        data={"question_index": "0", "answer": "false"}, follow_redirects=True,
    )
    assert 'aria-valuenow="13"' in page_text(first_hit)
    assert "CORRECT / HIT" in page_text(first_hit)
    assert COURSE["boss"][0]["explanation"] in page_text(first_hit)
    assert "回答する" not in page_text(first_hit)
    client.post(f"/learn/{COURSE_ID}/boss/next")
    term_hit = client.post(
        f"/learn/{COURSE_ID}/boss/answer",
        data={"question_index": "1", "answer": "Operating System"}, follow_redirects=True,
    )
    assert 'aria-valuenow="12"' in page_text(term_hit)
    client.post(f"/learn/{COURSE_ID}/boss/next")

    for index, question in enumerate(COURSE["boss"][2:], start=2):
        answer = str(question["answer"])
        client.post(
            f"/learn/{COURSE_ID}/boss/answer",
            data={"question_index": str(index), "answer": answer}, follow_redirects=True,
        )
        result = client.post(f"/learn/{COURSE_ID}/boss/next", follow_redirects=True)
    complete = page_text(result)
    assert "BOSS DEFEATED" in complete
    assert "14 / 14" in complete
    assert "COMPUTER & OS TRAINING COMPLETE" in complete
    assert "コンピュータ・OS基礎訓練 修了" in complete
    assert "Python基礎Ⅰ" in complete
    assert "準備中" in complete
    assert 'aria-disabled="true"' in complete
    assert "訓練選択へ戻る" in complete
    with client.session_transaction() as browser_session:
        assert browser_session["learn_progress"][COURSE_ID]["course_complete"] is True


def test_boss_wrong_answer_is_final_for_question_and_retry_starts_over(client):
    finish_all_units(client)
    client.post(f"/learn/{COURSE_ID}/boss/start")
    assert client.post(f"/learn/{COURSE_ID}/boss/next").location.endswith(f"/learn/{COURSE_ID}/")

    wrong = client.post(
        f"/learn/{COURSE_ID}/boss/answer",
        data={"question_index": "0", "answer": "true"}, follow_redirects=True,
    )
    page = page_text(wrong)
    assert "INCORRECT / ATTACK FAILED" in page
    assert "あなたの回答" in page
    assert "× 間違っている" in page
    assert COURSE["boss"][0]["explanation"] in page
    assert "回答する" not in page
    assert 'aria-valuenow="14"' in page
    assert "今回の正解数：0 / 14" in page

    client.post(f"/learn/{COURSE_ID}/boss/answer", data={"question_index": "0", "answer": "false"})
    reloaded = page_text(client.get(f"/learn/{COURSE_ID}/boss"))
    assert "INCORRECT" in reloaded
    assert 'aria-valuenow="14"' in reloaded
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["boss_correct_count"] == 0
        assert progress["boss_hp"] == 14

    second = client.post(f"/learn/{COURSE_ID}/boss/next", follow_redirects=True)
    assert "QUESTION 2 / 14" in page_text(second)
    client.post(f"/learn/{COURSE_ID}/boss/answer", data={"question_index": "0", "answer": "false"})
    for index, question in enumerate(COURSE["boss"][1:], start=1):
        client.post(
            f"/learn/{COURSE_ID}/boss/answer",
            data={"question_index": str(index), "answer": str(question["answer"])},
        )
        result = client.post(f"/learn/{COURSE_ID}/boss/next")
    assert result.location.endswith("/boss/result")
    failed = page_text(client.get(result.location))
    assert "BOSS BATTLE FAILED" in failed
    assert "13 / 14" in failed
    assert "SYSTEM CORE HP: 1 / 14" in failed
    assert "BOSSに再挑戦" in failed
    assert "教材を読み直す" in failed
    assert "訓練選択へ戻る" in failed
    assert client.get(f"/learn/{COURSE_ID}/complete").status_code == 302
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["course_complete"] is False
        assert len(progress["completed_lessons"]) == 6

    retry = client.post(f"/learn/{COURSE_ID}/boss/start", follow_redirects=True)
    assert "QUESTION 1 / 14" in page_text(retry)
    assert 'aria-valuenow="14"' in page_text(retry)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["boss_correct_count"] == 0
        assert progress["boss_answered"] is False
        assert progress["boss_result"] is None
        assert len(progress["completed_lessons"]) == 6
    for index, question in enumerate(COURSE["boss"]):
        client.post(
            f"/learn/{COURSE_ID}/boss/answer",
            data={"question_index": str(index), "answer": str(question["answer"])},
        )
        result = client.post(f"/learn/{COURSE_ID}/boss/next", follow_redirects=True)
    assert "BOSS DEFEATED" in page_text(result)
    assert "14 / 14" in page_text(result)


def test_boss_correct_answer_and_duplicate_post_change_hp_once(client):
    finish_all_units(client)
    client.post(f"/learn/{COURSE_ID}/boss/start")
    first = client.post(
        f"/learn/{COURSE_ID}/boss/answer",
        data={"question_index": "0", "answer": "false"}, follow_redirects=True,
    )
    assert "CORRECT / HIT" in page_text(first)
    assert "次の問題へ" in page_text(first)
    assert 'aria-valuenow="13"' in page_text(first)
    client.post(f"/learn/{COURSE_ID}/boss/answer", data={"question_index": "0", "answer": "false"})
    assert 'aria-valuenow="13"' in page_text(client.get(f"/learn/{COURSE_ID}/boss"))
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["boss_correct_count"] == 1
        assert progress["boss_hp"] == 13
    client.post(f"/learn/{COURSE_ID}/boss/next")
    client.post(f"/learn/{COURSE_ID}/boss/next")
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["boss_index"] == 1
        assert progress["boss_correct_count"] == 1


def test_dev_shortcut_uses_same_unit_and_boss_progress(client, monkeypatch):
    monkeypatch.setenv("LEARN_DEV_SHORTCUT", "1")
    first_lesson = COURSE["lessons"][0]
    first_result = finish_unit(client, first_lesson, use_shortcut=True)
    assert "TRAINING COMPLETE" in page_text(client.get(first_result.location))
    assert "6 / 6" in page_text(client.get(first_result.location))
    assert client.get(f"/learn/{COURSE_ID}/os/").status_code == 200

    for lesson in COURSE["lessons"][1:]:
        finish_unit(client, lesson, use_shortcut=True)
    client.post(f"/learn/{COURSE_ID}/boss/start")
    assert "DEV MODE" in page_text(client.get(f"/learn/{COURSE_ID}/boss"))
    for index in range(len(COURSE["boss"])):
        client.post(
            f"/learn/{COURSE_ID}/boss/answer",
            data={"question_index": str(index), "action": "dev_skip"},
            follow_redirects=True,
        )
        result = client.post(f"/learn/{COURSE_ID}/boss/next", follow_redirects=True)
    assert "コンピュータ・OS基礎訓練 修了" in page_text(result)
    assert "14 / 14" in page_text(result)
    with client.session_transaction() as browser_session:
        progress = browser_session["learn_progress"][COURSE_ID]
        assert progress["boss_correct_count"] == 14
        assert progress["boss_hp"] == 0
        assert progress["course_complete"] is True
