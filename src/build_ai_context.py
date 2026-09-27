"""AIへ渡す情報だけを選び、機密値の除去と文字数制限を行う。"""

import os
import re
from http.cookies import SimpleCookie

REDACTED = "[REDACTED]"
# よくある代入・JSON・ログ表記。完全な秘密検出ではないため、UIでも入力しないよう案内する。
SECRET_FIELD = re.compile(
    r'''(?im)(?<![\w.])(?:[\w.\["']{0,120}(?:api[_-]?key|secret(?:[_-]?key)?|password|passwd|access[_-]?token|csrf[_-]?token|cookie)[\w.\]"']{0,120})\s*[:=]\s*(?:["']([^"'\r\n]+)["']|([^\s,;}]+))'''
)


def secret_values(project, extra=()):
    values = [os.environ.get("OPENAI_API_KEY"), os.environ.get("FLASK_SECRET_KEY"),
              project.get("runtime_secret"), *extra]
    cookie = project.get("runtime_state", {}).get("cookie", "")
    values.append(cookie)
    parsed = SimpleCookie()
    try:
        parsed.load(cookie)
        values.extend(item.value for item in parsed.values())
    except Exception:
        pass
    # 同じハードコード値がログや質問にも現れた場合に除去できるよう収集する。
    for code in project["files"].values():
        for match in SECRET_FIELD.finditer(code):
            values.append(match.group(1) or match.group(2))
    return tuple(value for value in values if isinstance(value, str) and value)


def redact(text, secrets=()):
    text = str(text)
    for value in sorted(set(secrets), key=len, reverse=True):
        text = text.replace(value, REDACTED)
    text = re.sub(r"-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|\Z)",
                  REDACTED, text, flags=re.S)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{8,}", REDACTED, text)
    text = re.sub(r"(?im)\b(?:authorization|set-cookie|cookie)\s*:\s*[^\r\n]+", REDACTED, text)
    text = re.sub(r"(?i)\bBearer\s+[^\s\"']+", "Bearer " + REDACTED, text)
    return SECRET_FIELD.sub(lambda m: m.group(0).replace(m.group(1) or m.group(2), REDACTED), text)


def safe_history(history, secrets=(), count=20, per_message=6000):
    return [{"role": item["role"], "text": redact(item["text"], secrets)[:per_message]}
            for item in history[-count:] if item.get("role") in {"user", "assistant"}]


def learn_index():
    # 教材本文・問題・進捗は送らず、既存の正式順序とUNIT見出しだけを使う。
    from src.learn_data import COURSES
    from src.learn_routes import FORMAL_COURSE_IDS

    return "\n".join(
        f"第{number}訓練 {COURSES[key]['title']}: "
        + " / ".join(lesson["title"] for lesson in COURSES[key]["lessons"])[:160]
        for number, key in enumerate(FORMAL_COURSE_IDS, 1)
    )[:2800]


def make_context(project, active_file, preview=None, secrets=()):
    preview = preview if isinstance(preview, dict) else {}
    last = preview.get("last_run")
    last = last if isinstance(last, dict) else {}
    mode = preview.get("mode")
    run_mode = last.get("mode")
    status = last.get("status")
    logs = last.get("logs", "")
    revision = last.get("revision")
    return {
        "project_name": redact(project["name"], secrets)[:80],
        "files": [redact(name, secrets)[:120] for name in list(project["files"])[:30]],
        "active_file": redact(active_file, secrets)[:120],
        "code": redact(project["files"].get(active_file, ""), secrets)[:6000],
        "code_truncated": len(project["files"].get(active_file, "")) > 6000,
        "run_mode": mode if mode in ("html", "flask") else "未確認",
        "saved_revision": project["revision"],
        "preview_report": {
            "source": "ブラウザーからの申告。現在のコードの検証結果とは限らない。",
            "mode": run_mode if run_mode in ("html", "flask") else "未確認",
            "status": status if type(status) is int and 100 <= status <= 599 else "未確認・実行失敗",
            "revision": revision if type(revision) is int and 0 < revision < 1_000_000_000 else None,
            "logs": redact(logs, secrets)[-2000:] if isinstance(logs, str) else "",
        },
        "learn_topics": learn_index(),
    }
