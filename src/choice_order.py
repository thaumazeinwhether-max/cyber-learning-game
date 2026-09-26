"""4択の並びを、再起動しても変わらない順序に整える。"""

import hashlib
import random


def arrange_choices(course):
    """問題文から固定の並びを作り、正解番号も一緒に更新する。"""
    course_number = course["curriculum_number"]
    for lesson in course["lessons"]:
        for question in lesson["questions"]:
            if "options" in question:
                _arrange_question(question, f"{course_number}:{lesson['id']}:{question['prompt']}")
    for question in course["boss"]:
        if "options" in question:
            _arrange_question(question, f"{course_number}:boss:{question['prompt']}")


def _arrange_question(question, key):
    original_options = question["options"]
    original_answer = question["answer"]
    positions = list(range(len(original_options)))
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    random.Random(int.from_bytes(digest, "big")).shuffle(positions)
    question["options"] = [original_options[position] for position in positions]
    question["answer"] = positions.index(original_answer)
