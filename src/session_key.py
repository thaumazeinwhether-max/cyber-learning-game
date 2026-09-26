"""Learn進捗の署名に使う鍵を、ローカル開発環境で再利用する。"""

import os
import secrets
import time
from pathlib import Path


def load_session_key(instance_path):
    """環境変数を優先し、未設定ならGit管理外のローカル鍵を使う。"""
    configured_key = os.environ.get("FLASK_SECRET_KEY")
    if configured_key:
        return configured_key

    key_file = Path(instance_path) / "learn_secret_key"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        # 排他的作成で、同時起動した二つのプロセスが別の鍵を作らないようにする。
        descriptor = os.open(key_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(secrets.token_hex(32))

    # 別プロセスが作成直後で書き込み中の場合だけ、短く待って読み直す。
    for _ in range(20):
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            return key
        time.sleep(0.01)
    raise RuntimeError(f"セッション署名鍵が空です: {key_file}")
