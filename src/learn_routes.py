"""Learnフェーズの画面遷移と進捗管理。"""

import os

from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from src.answer_check import is_correct
from src.learn_data import COURSES, get_lesson


learn = Blueprint("learn", __name__, url_prefix="/learn")

# 正式訓練だけを順番に解放する。初期版の体験コースは従来どおり利用可能。
FORMAL_COURSE_IDS = (
    "computer_os", "python_basics_1", "network_basics", "web_http",
    "python_basics_2", "web_creation", "flask_basics",
)


def dev_mode():
    return os.environ.get("LEARN_DEV_SHORTCUT") == "1"


@learn.app_context_processor
def add_dev_mode_to_templates():
    return {"dev_mode": dev_mode()}


def get_course(course_id):
    course = COURSES.get(course_id)
    if course is None:
        abort(404)
    if not course_unlocked(course_id):
        abort(403)
    return course


def course_unlocked(course_id):
    if course_id not in FORMAL_COURSE_IDS:
        return True
    index = FORMAL_COURSE_IDS.index(course_id)
    if index == 0:
        return True
    previous_id = FORMAL_COURSE_IDS[index - 1]
    return session.get("learn_progress", {}).get(previous_id, {}).get("course_complete", False)


def get_progress(course_id):
    all_progress = session.get("learn_progress", {})
    defaults = {
        "completed_lessons": [],
        "active_lesson": None,
        "question_index": 0,
        "correct_count": 0,
        "question_answered": False,
        "question_correct": False,
        "submitted_answer": "",
        "attempt_result": None,
        "boss_started": False,
        "boss_index": 0,
        "boss_correct_count": 0,
        "boss_answered": False,
        "boss_correct": False,
        "boss_submitted_answer": "",
        "boss_submitted_code": "",
        "boss_hp": len(COURSES[course_id]["boss"]),
        "boss_result": None,
        "course_complete": False,
    }
    # 以前の版のCookieに新しい項目がなくても、既定値を補って表示できる。
    return {**defaults, **all_progress.get(course_id, {})}


def save_progress(course_id, progress):
    all_progress = session.get("learn_progress", {})
    all_progress[course_id] = progress
    session["learn_progress"] = all_progress


def lessons_finished(course, progress):
    return all(
        lesson["id"] in progress["completed_lessons"]
        for lesson in course["lessons"]
    )


def lesson_unlocked(course, progress, lesson_id):
    lesson_ids = [lesson["id"] for lesson in course["lessons"]]
    lesson_number = lesson_ids.index(lesson_id)
    return lesson_number == 0 or lesson_ids[lesson_number - 1] in progress["completed_lessons"]


def get_visible_lesson(course_id, lesson_id):
    course = get_course(course_id)
    lesson = get_lesson(course, lesson_id)
    if lesson is None:
        abort(404)
    progress = get_progress(course_id)
    if not lesson_unlocked(course, progress, lesson_id):
        return course, lesson, progress, False
    return course, lesson, progress, True


@learn.route("/")
def home():
    unlocked_courses = {course_id: course_unlocked(course_id) for course_id in COURSES}
    return render_template("learn_home.html", courses=COURSES,
                           unlocked_courses=unlocked_courses)


@learn.route("/<course_id>/")
def course_home(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    return render_template(
        "course.html", course=course, course_id=course_id, progress=progress,
        boss_unlocked=lessons_finished(course, progress),
    )


@learn.route("/<course_id>/<lesson_id>/")
def lesson_page(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked:
        return redirect(url_for("learn.course_home", course_id=course_id))
    return render_template(
        "lesson.html", course=course, course_id=course_id,
        lesson=lesson, completed=lesson_id in progress["completed_lessons"],
    )


@learn.post("/<course_id>/<lesson_id>/start")
def start_lesson(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked:
        return redirect(url_for("learn.course_home", course_id=course_id))
    progress["active_lesson"] = lesson_id
    progress["question_index"] = 0
    progress["correct_count"] = 0
    progress["question_answered"] = False
    progress["question_correct"] = False
    progress["submitted_answer"] = ""
    progress["attempt_result"] = None
    save_progress(course_id, progress)
    return redirect(url_for("learn.battle", course_id=course_id, lesson_id=lesson_id))


@learn.route("/<course_id>/<lesson_id>/battle")
def battle(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id:
        return redirect(url_for("learn.lesson_page", course_id=course_id, lesson_id=lesson_id))
    question = lesson["questions"][progress["question_index"]]
    question_mode = question.get("mode", course["question_mode"])
    if question_mode == "choice":
        correct_answer = question["options"][question["answer"]]
        selected_index = progress.get("submitted_answer", "")
        if selected_index.isdecimal() and int(selected_index) < len(question["options"]):
            submitted_answer = question["options"][int(selected_index)]
        else:
            submitted_answer = "未選択"
        wrong_explanation = question.get("wrong_explanations", {}).get(
            selected_index, question.get("hint", "")
        )
    else:
        correct_answer = question["answer"]
        submitted_answer = progress.get("submitted_answer", "") or "未入力"
        wrong_explanation = question.get("hint", "")
    return render_template(
        "battle.html", course=course, course_id=course_id, lesson=lesson,
        progress=progress, question=question, correct_answer=correct_answer,
        submitted_answer=submitted_answer, wrong_explanation=wrong_explanation,
        question_mode=question_mode,
    )


@learn.post("/<course_id>/<lesson_id>/answer")
def answer_battle(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    battle_url = url_for("learn.battle", course_id=course_id, lesson_id=lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id:
        return redirect(url_for("learn.lesson_page", course_id=course_id, lesson_id=lesson_id))
    if progress.get("question_answered") or request.form.get("question_index") != str(progress["question_index"]):
        return redirect(battle_url)

    question = lesson["questions"][progress["question_index"]]
    shortcut = dev_mode() and request.form.get("action") == "dev_skip"
    answer = request.form.get("answer", "")[:1000]
    correct = shortcut or is_correct(course_id, question, answer)
    progress["question_answered"] = True
    progress["question_correct"] = correct
    progress["submitted_answer"] = answer
    if correct:
        progress["correct_count"] += 1
    save_progress(course_id, progress)
    return redirect(battle_url)


@learn.post("/<course_id>/<lesson_id>/next")
def next_enemy(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id or not progress.get("question_answered"):
        return redirect(url_for("learn.course_home", course_id=course_id))

    next_index = progress["question_index"] + 1
    if next_index < len(lesson["questions"]):
        progress["question_index"] = next_index
        progress["question_answered"] = False
        progress["question_correct"] = False
        progress["submitted_answer"] = ""
        save_progress(course_id, progress)
        return redirect(url_for("learn.battle", course_id=course_id, lesson_id=lesson_id))

    passed = progress["correct_count"] == len(lesson["questions"])
    progress["attempt_result"] = {
        "lesson_id": lesson_id,
        "correct_count": progress["correct_count"],
        "total": len(lesson["questions"]),
        "passed": passed,
    }
    if passed and lesson_id not in progress["completed_lessons"]:
        progress["completed_lessons"].append(lesson_id)
    progress["active_lesson"] = None
    progress["question_answered"] = False
    save_progress(course_id, progress)
    if not passed:
        return redirect(url_for("learn.lesson_result", course_id=course_id, lesson_id=lesson_id))
    return redirect(url_for("learn.lesson_complete", course_id=course_id, lesson_id=lesson_id))


@learn.route("/<course_id>/<lesson_id>/result")
def lesson_result(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked:
        return redirect(url_for("learn.course_home", course_id=course_id))
    result = progress.get("attempt_result")
    if not result or result["lesson_id"] != lesson_id or result["passed"]:
        return redirect(url_for("learn.lesson_page", course_id=course_id, lesson_id=lesson_id))
    return render_template(
        "lesson_result.html", course=course, course_id=course_id,
        lesson=lesson, result=result,
    )


@learn.route("/<course_id>/<lesson_id>/complete")
def lesson_complete(course_id, lesson_id):
    course = get_course(course_id)
    lesson = get_lesson(course, lesson_id)
    if lesson is None:
        abort(404)
    progress = get_progress(course_id)
    if lesson_id not in progress["completed_lessons"]:
        return redirect(url_for("learn.course_home", course_id=course_id))

    lesson_ids = [item["id"] for item in course["lessons"]]
    lesson_number = lesson_ids.index(lesson_id)
    next_lesson = None
    if lesson_number + 1 < len(lesson_ids):
        next_lesson = course["lessons"][lesson_number + 1]
    return render_template(
        "lesson_complete.html", course=course, course_id=course_id,
        lesson=lesson, next_lesson=next_lesson,
    )


@learn.post("/<course_id>/boss/start")
def start_boss(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    if not lessons_finished(course, progress):
        return redirect(url_for("learn.course_home", course_id=course_id))
    if progress["course_complete"]:
        return redirect(url_for("learn.complete", course_id=course_id))
    progress["boss_started"] = True
    progress["boss_index"] = 0
    progress["boss_correct_count"] = 0
    progress["boss_answered"] = False
    progress["boss_correct"] = False
    progress["boss_submitted_answer"] = ""
    progress["boss_submitted_code"] = ""
    progress["boss_hp"] = len(course["boss"])
    progress["boss_result"] = None
    save_progress(course_id, progress)
    return redirect(url_for("learn.boss", course_id=course_id))


@learn.route("/<course_id>/boss")
def boss(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    if progress["course_complete"]:
        return redirect(url_for("learn.complete", course_id=course_id))
    if not lessons_finished(course, progress) or not progress["boss_started"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    question = course["boss"][progress["boss_index"]]
    answer = progress.get("boss_submitted_answer", "")
    question_mode = question.get("mode", course["question_mode"])
    if question_mode == "choice":
        if question["type"] == "true_false":
            correct_answer = "○ 正しい" if question["answer"] == "true" else "× 間違っている"
            submitted_answer = {"true": "○ 正しい", "false": "× 間違っている"}.get(answer, "未選択")
        elif question.get("options"):
            correct_answer = question["options"][question["answer"]]
            if answer.isdecimal() and int(answer) < len(question["options"]):
                submitted_answer = question["options"][int(answer)]
            else:
                submitted_answer = "未選択"
        else:
            correct_answer = question["answer"]
            submitted_answer = answer or "未入力"
    else:
        correct_answer = "正しい" if question["valid"] else "間違っている"
        submitted_answer = {"correct": "正しい", "incorrect": "間違っている"}.get(answer, "未選択")
    wrong_explanation = question.get("wrong_explanations", {}).get(
        answer, question.get("hint", "")
    )
    return render_template(
        "boss.html", course=course, course_id=course_id,
        progress=progress, question=question, max_hp=len(course["boss"]),
        correct_answer=correct_answer, submitted_answer=submitted_answer,
        wrong_explanation=wrong_explanation, question_mode=question_mode,
    )


@learn.post("/<course_id>/boss/answer")
def answer_boss(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    boss_url = url_for("learn.boss", course_id=course_id)
    if not lessons_finished(course, progress) or not progress["boss_started"] or progress["course_complete"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    if progress.get("boss_answered") or request.form.get("question_index") != str(progress["boss_index"]):
        return redirect(boss_url)

    question = course["boss"][progress["boss_index"]]
    shortcut = dev_mode() and request.form.get("action") == "dev_skip"
    answer = request.form.get("answer", "")[:1000]
    corrected_code = request.form.get("corrected_code", "")[:1000]
    correct = shortcut or is_correct(
        course_id, question, answer, corrected_code
    )
    progress["boss_answered"] = True
    progress["boss_correct"] = correct
    progress["boss_submitted_answer"] = answer
    progress["boss_submitted_code"] = corrected_code
    if correct:
        progress["boss_correct_count"] += 1
        progress["boss_hp"] -= 1
    save_progress(course_id, progress)
    return redirect(boss_url)


@learn.post("/<course_id>/boss/next")
def next_boss_question(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    if not lessons_finished(course, progress) or not progress["boss_started"] or not progress.get("boss_answered"):
        return redirect(url_for("learn.course_home", course_id=course_id))

    next_index = progress["boss_index"] + 1
    if next_index < len(course["boss"]):
        progress["boss_index"] = next_index
        progress["boss_answered"] = False
        progress["boss_correct"] = False
        progress["boss_submitted_answer"] = ""
        progress["boss_submitted_code"] = ""
        save_progress(course_id, progress)
        return redirect(url_for("learn.boss", course_id=course_id))

    passed = progress["boss_correct_count"] == len(course["boss"])
    progress["boss_result"] = {
        "correct_count": progress["boss_correct_count"],
        "total": len(course["boss"]),
        "hp": progress["boss_hp"],
        "passed": passed,
    }
    progress["boss_started"] = False
    progress["boss_answered"] = False
    if passed:
        progress["course_complete"] = True
    save_progress(course_id, progress)
    if passed:
        return redirect(url_for("learn.complete", course_id=course_id))
    return redirect(url_for("learn.boss_result", course_id=course_id))


@learn.route("/<course_id>/boss/result")
def boss_result(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    result = progress.get("boss_result")
    if not lessons_finished(course, progress) or not result or result["passed"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    return render_template("boss_result.html", course=course, course_id=course_id, result=result)


@learn.route("/<course_id>/complete")
def complete(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    if not progress["course_complete"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    next_course_id = None
    next_course = None
    if course_id in FORMAL_COURSE_IDS:
        index = FORMAL_COURSE_IDS.index(course_id)
        if index + 1 < len(FORMAL_COURSE_IDS):
            next_course_id = FORMAL_COURSE_IDS[index + 1]
            next_course = COURSES[next_course_id]
    return render_template("complete.html", course=course, course_id=course_id,
                           next_course=next_course, next_course_id=next_course_id)
