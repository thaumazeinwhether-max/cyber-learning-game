"""第10〜12訓練で共通する、教材ブロックと知識問題の小さな補助関数。"""

from src.chapter_blocks import code, flow, key_points, paragraph, section, table, warning
from src.choice_order import arrange_choices


def chapter(*, objective, why, connection, concept, mechanism, comparison,
            example, misunderstanding, defense, points, steps=(), sample=None):
    """本文は呼び出し側に置き、同じ章立てで表示する。"""
    definition_blocks = [paragraph(concept), paragraph(mechanism)]
    if comparison:
        definition_blocks.append(table(comparison[0], comparison[1]))

    example_blocks = []
    if steps:
        example_blocks.append(flow(*steps))
    if sample:
        example_blocks.append(code(sample[0], sample[1], sample[2]))
    example_blocks.extend([paragraph(example), warning(misunderstanding)])

    return {
        "objective": objective,
        "why": why,
        "connection": connection,
        "sections": [
            section("用語と仕組み", *definition_blocks),
            section("具体例と判断", *example_blocks),
            section("防御・運用のポイント",
                    paragraph(defense),
                    key_points(*points)),
        ],
    }


def choice(prompt, right, wrong1, wrong2, wrong3, explanation, source=None):
    item = {
        "type": "application",
        "prompt": prompt,
        "options": [right, wrong1, wrong2, wrong3],
        "answer": 0,
        "explanation": explanation,
    }
    if source:
        item["code"] = source
    return item


def true_false(prompt, answer, explanation):
    return {
        "type": "true_false", "prompt": prompt,
        "answer": answer, "explanation": explanation,
    }


def term(prompt, answer, explanation, *aliases):
    return {
        "type": "term", "prompt": prompt, "answer": answer,
        "accepted_answers": [answer, *aliases], "explanation": explanation,
    }


def prepare_course(course, chapters):
    """本文を対応するUNITへ付け、4択の選択肢を安定した順序にする。"""
    for lesson in course["lessons"]:
        lesson.update(chapters[lesson["id"]])
    arrange_choices(course)

    for question in (
        [item for lesson in course["lessons"] for item in lesson["questions"]]
        + course["boss"]
    ):
        if "options" in question:
            correct_option = question["options"][question["answer"]]
            question["wrong_explanations"] = {
                str(index): f"「{option}」はこの状況の答えではありません。{question['explanation']} 正しい選択肢は「{correct_option}」です。"
                for index, option in enumerate(question["options"])
                if index != question["answer"]
            }
