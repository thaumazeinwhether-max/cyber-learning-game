"""Learnフェーズの画面遷移と進捗管理。"""

import os

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from src.answer_check import is_correct
from src.learn_data import COURSES, get_lesson


learn = Blueprint("learn", __name__, url_prefix="/learn")


def dev_mode():
    return os.environ.get("LEARN_DEV_SHORTCUT") == "1"


@learn.app_context_processor
def add_dev_mode_to_templates():
    return {"dev_mode": dev_mode()}


def get_course(course_id):
    course = COURSES.get(course_id)
    if course is None:
        abort(404)
    return course


def get_progress(course_id):
    all_progress = session.get("learn_progress", {})
    return all_progress.get(course_id, {
        "completed_lessons": [],
        "active_lesson": None,
        "question_index": 0,
        "enemy_defeated": False,
        "boss_started": False,
        "boss_index": 0,
        "boss_hp": 3,
        "course_complete": False,
    })


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
    return render_template("learn_home.html", courses=COURSES)


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
    progress["enemy_defeated"] = False
    save_progress(course_id, progress)
    return redirect(url_for("learn.battle", course_id=course_id, lesson_id=lesson_id))


@learn.route("/<course_id>/<lesson_id>/battle")
def battle(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id:
        return redirect(url_for("learn.lesson_page", course_id=course_id, lesson_id=lesson_id))
    question = lesson["questions"][progress["question_index"]]
    return render_template(
        "battle.html", course=course, course_id=course_id, lesson=lesson,
        progress=progress, question=question,
    )


@learn.post("/<course_id>/<lesson_id>/answer")
def answer_battle(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    battle_url = url_for("learn.battle", course_id=course_id, lesson_id=lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id:
        return redirect(url_for("learn.lesson_page", course_id=course_id, lesson_id=lesson_id))
    if progress["enemy_defeated"] or request.form.get("question_index") != str(progress["question_index"]):
        return redirect(battle_url)

    question = lesson["questions"][progress["question_index"]]
    shortcut = dev_mode() and request.form.get("action") == "dev_skip"
    correct = shortcut or is_correct(course_id, question, request.form.get("answer", ""))
    if correct:
        progress["enemy_defeated"] = True
        save_progress(course_id, progress)
        flash("HIT / 攻撃成功！ 敵を倒しました。", "success")
    else:
        flash("WARNING / ATTACK FAILED。不正解。" + question["explanation"] + " もう一度答えられます。", "error")
    return redirect(battle_url)


@learn.post("/<course_id>/<lesson_id>/next")
def next_enemy(course_id, lesson_id):
    course, lesson, progress, unlocked = get_visible_lesson(course_id, lesson_id)
    if not unlocked or progress["active_lesson"] != lesson_id or not progress["enemy_defeated"]:
        return redirect(url_for("learn.course_home", course_id=course_id))

    next_index = progress["question_index"] + 1
    if next_index < len(lesson["questions"]):
        progress["question_index"] = next_index
        progress["enemy_defeated"] = False
        save_progress(course_id, progress)
        return redirect(url_for("learn.battle", course_id=course_id, lesson_id=lesson_id))

    if lesson_id not in progress["completed_lessons"]:
        progress["completed_lessons"].append(lesson_id)
    progress["active_lesson"] = None
    save_progress(course_id, progress)
    return redirect(url_for("learn.lesson_complete", course_id=course_id, lesson_id=lesson_id))


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
    if not progress["boss_started"]:
        progress["boss_started"] = True
        progress["boss_index"] = 0
        progress["boss_hp"] = len(course["boss"])
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
    return render_template(
        "boss.html", course=course, course_id=course_id,
        progress=progress, question=course["boss"][progress["boss_index"]],
        max_hp=len(course["boss"]),
    )


@learn.post("/<course_id>/boss/answer")
def answer_boss(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    boss_url = url_for("learn.boss", course_id=course_id)
    if not lessons_finished(course, progress) or not progress["boss_started"] or progress["course_complete"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    if request.form.get("question_index") != str(progress["boss_index"]):
        return redirect(boss_url)

    question = course["boss"][progress["boss_index"]]
    shortcut = dev_mode() and request.form.get("action") == "dev_skip"
    correct = shortcut or is_correct(
        course_id, question, request.form.get("answer", ""), request.form.get("corrected_code", "")
    )
    if correct:
        progress["boss_hp"] -= 1
        progress["boss_index"] += 1
        if progress["boss_hp"] == 0:
            progress["course_complete"] = True
            save_progress(course_id, progress)
            return redirect(url_for("learn.complete", course_id=course_id))
        save_progress(course_id, progress)
        flash("HIT / 攻撃成功！ ボスHPが1減りました。次の問題へ進みます。", "success")
    else:
        flash("WARNING / ATTACK FAILED。不正解。" + question["explanation"] + " もう一度答えられます。", "error")
    return redirect(boss_url)


@learn.route("/<course_id>/complete")
def complete(course_id):
    course = get_course(course_id)
    progress = get_progress(course_id)
    if not progress["course_complete"]:
        return redirect(url_for("learn.course_home", course_id=course_id))
    return render_template("complete.html", course=course, course_id=course_id)
