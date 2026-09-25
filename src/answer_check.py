"""回答の判定。入力されたPythonコードは解析だけ行い、実行しない。"""

import ast

from src.learn_data import COURSES


def same_python_code(submitted_code, expected_code):
    if not submitted_code or len(submitted_code) > 1000:
        return False

    try:
        submitted_tree = ast.parse(submitted_code)
        expected_tree = ast.parse(expected_code)
    except (SyntaxError, ValueError, RecursionError):
        return False

    # 文字列の引用符や空白はASTに残らないため、同じ構文なら同じ正解になる。
    return ast.dump(submitted_tree) == ast.dump(expected_tree)


def is_correct(course_id, question, answer, corrected_code=""):
    if COURSES[course_id]["question_mode"] == "choice":
        if question.get("type") == "true_false":
            return answer == question["answer"]
        if question.get("type") == "term":
            accepted_answers = question.get("accepted_answers", [question["answer"]])
            normalized_answer = "".join(answer.casefold().split())
            return any(
                normalized_answer == "".join(accepted.casefold().split())
                for accepted in accepted_answers
            )
        return answer == str(question["answer"])

    if question.get("type") == "debug":
        if question["valid"]:
            return answer == "correct"
        return answer == "incorrect" and same_python_code(
            corrected_code, question["answer"]
        )

    return same_python_code(answer, question["answer"])
