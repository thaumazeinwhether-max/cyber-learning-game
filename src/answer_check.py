"""回答の判定。入力されたPythonコードは解析だけ行い、実行しない。"""

import ast


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
    if course_id == "it":
        if question.get("type") == "true_false":
            return answer == question["answer"]
        if question.get("type") == "term":
            return answer.strip().casefold() == question["answer"]
        return answer == str(question["answer"])

    if question.get("type") == "debug":
        if question["valid"]:
            return answer == "correct"
        return answer == "incorrect" and same_python_code(
            corrected_code, question["answer"]
        )

    return same_python_code(answer, question["answer"])
