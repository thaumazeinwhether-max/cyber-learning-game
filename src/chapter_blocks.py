"""参考書型UNITの本文で使う、単純な教材ブロック。

返す辞書の形は第1訓練と同じ。lesson.html が表示方法を担当する。
"""


def section(heading, *blocks):
    return {"heading": heading, "blocks": list(blocks)}


def paragraph(text):
    return {"type": "paragraph", "text": text}


def bullets(*items):
    return {"type": "bullets", "items": list(items)}


def table(columns, rows):
    return {"type": "table", "columns": columns, "rows": rows}


def code(source, caption, language="text"):
    return {"type": "code", "code": source, "caption": caption, "language": language}


def flow(*steps):
    return {"type": "flow", "steps": list(steps)}


def note(title, text):
    return {"type": "note", "title": title, "text": text}


def warning(text):
    return {"type": "warning", "title": "よくある勘違い", "text": text}


def key_points(*items):
    return {"type": "key_points", "items": list(items)}
