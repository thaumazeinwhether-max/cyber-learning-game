"""専用Linuxコンテナーの入口。ゲーム本体からimportしてはいけない。"""

import base64
import contextlib
import io
import json
import logging
import os
import runpy
import stat
import sys
import traceback
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask


class LimitedLog(io.StringIO):
    def write(self, text):
        room = max(0, 8000 - self.tell())
        super().write(str(text)[:room])
        return len(text)


def main(root=Path("/workspace")):
    bundle = json.loads(sys.stdin.buffer.read(4_000_000))
    for name, code in bundle["files"].items():
        target = root / name
        if not target.resolve().is_relative_to(root) or name.startswith("data/"):
            raise ValueError("Invalid project path")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "app.sqlite3"
    previous_state = bundle.get("state", {})
    if previous_state.get("database"):
        db_path.write_bytes(base64.b64decode(previous_state["database"], validate=True))
    os.environ["BUILD_APP_SECRET"] = bundle["secret"]
    sys.path.insert(0, str(root))
    logs = LimitedLog()
    cookies = SimpleCookie()
    cookies.load(previous_state.get("cookie", ""))
    result = {"html": "", "status": 500, "state": previous_state}
    with contextlib.redirect_stdout(logs), contextlib.redirect_stderr(logs):
        try:
            module = runpy.run_path(str(root / "app.py"), run_name="build_application")
            app = module.get("app")
            if not isinstance(app, Flask):
                raise ValueError("app.pyには app = Flask(__name__) を用意してください。")
            app.secret_key = app.secret_key or bundle["secret"]
            app.config.update(TESTING=True, DEBUG=False)
            handler = logging.StreamHandler(logs)
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.INFO)
            client = app.test_client(use_cookies=False)
            path, method, data = bundle["path"], bundle["method"], bundle["data"]
            for _ in range(6):
                cookie_header = "; ".join(f"{key}={value.coded_value}" for key, value in cookies.items())
                response = client.open(path, method=method, data=data if method == "POST" else None,
                                       query_string=data if method == "GET" and data else None,
                                       base_url="http://build.local", headers={"Cookie": cookie_header})
                logs.write(f"{method} {path} -> {response.status_code}\n")
                for value in response.headers.getlist("Set-Cookie"):
                    cookies.load(value)
                if response.status_code not in {301, 302, 303, 307, 308}:
                    break
                destination = response.headers.get("Location", "/")
                parts = urlsplit(destination)
                if parts.scheme or parts.netloc or "\\" in destination:
                    raise ValueError("外部URLへのリダイレクトはプレビューでは使えません。")
                path = destination
                if response.status_code in {301, 302, 303}:
                    method, data = "GET", {}
            else:
                raise ValueError("リダイレクトが多すぎます。")
            result.update(html=response.get_data(as_text=True)[:300_000], status=response.status_code)
            result["state"] = {"cookie": "; ".join(f"{key}={value.coded_value}" for key, value in cookies.items())}
            if db_path.exists():
                # 利用者がDBをシンボリックリンクや特殊ファイルに置換しても読み出さない。
                descriptor = os.open(db_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(descriptor, "rb") as file:
                    info = os.fstat(file.fileno())
                    if not stat.S_ISREG(info.st_mode) or info.st_size > 1_000_000:
                        raise ValueError("保存できるDBは通常ファイル・1MBまでです。")
                    result["state"]["database"] = base64.b64encode(file.read(1_000_001)).decode("ascii")
        except Exception:
            traceback.print_exc(limit=8)
            result.update(html="<h1>実行エラー</h1><p>Build画面の実行ログを確認してください。</p>", status=500,
                          state=previous_state)
    result["logs"] = logs.getvalue()
    sys.stdout.write(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
