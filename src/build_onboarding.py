"""初回のアイデア整理。仕様を決定せず、編集可能な4項目だけを提案する。"""

import json

PLAN_KEYS = ("purpose", "features", "learn", "first_step")


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != set(PLAN_KEYS):
        raise ValueError("ガイドの4項目を確認してください。")
    if any(not isinstance(value, str) or len(value) > 1500 for value in plan.values()):
        raise ValueError("ガイドの各項目は1500文字以内で入力してください。")
    return {key: plan[key].strip() for key in PLAN_KEYS}


def parse_plan(answer):
    try:
        plan = validate_plan(json.loads(answer))
        if not all(plan.values()):
            raise ValueError("Empty proposal")
        return plan
    except (ValueError, TypeError):
        # providerの返答本文や内部例外は利用者・ログへ流さない。
        raise ValueError("ガイドの整理結果を取得できませんでした。") from None


def local_plan(context, idea):
    """キーワードで候補を絞る。未知の題材は入力を保持し、共通の出発点を示す。"""
    records = any(word in idea.lower() for word in ("記録", "保存", "管理", "メモ", "日記", "record"))
    inputs = records or any(word in idea for word in ("入力", "検索", "計算", "フォーム"))
    features = "・目的が伝わるトップページ\n・必要な情報を読みやすく表示する画面"
    learn = "第6訓練：HTML / CSSで画面を作る"
    if inputs:
        features += "\n・必要な項目だけを入力するフォーム"
        learn += "\n第4・7訓練：HTTPのPOSTとFlaskで入力を受け取る"
    if records:
        features += "\n・入力した記録の保存と一覧（必要になった段階で）"
        learn += "\n第8訓練：SQLiteと安全なSQLで保存する"
    if "templates/index.html" in context["files"]:
        first = "templates/index.html の見出しと説明を、このアプリの目的に合わせて自分で変更し、SAVE → HTML / CSSモードでRUNして表示を確認しましょう。"
    else:
        first = "現在のHTMLファイルを選び、見出しと目的を表す説明を1つ書いてSAVE → HTML / CSSモードでRUNしましょう。HTMLファイルがなければ「＋ ファイル」から作れます。"
    return {"purpose": idea, "features": features,
            "learn": learn, "first_step": first}
