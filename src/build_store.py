"""Buildだけの保存領域。利用者のパスをホスト上のファイル名にしない。"""

import json
import re
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

from src.build_starter import STARTER_FILES

MAX_FILES = 30
MAX_FILE_BYTES = 100_000
MAX_PROJECT_BYTES = 500_000
EXTENSIONS = {".py", ".html", ".css", ".js", ".sql", ".md", ".txt", ".json"}


def validate_files(files):
    if not isinstance(files, dict) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError("ファイルは1〜30個で保存してください。")
    total = 0
    for name, content in files.items():
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_./-]{0,119}", name):
            raise ValueError("ファイル名は英数字・_・-・/・. を使ってください。")
        parts = name.split("/")
        if any(part in {"", ".", ".."} or part.startswith(".") for part in parts):
            raise ValueError("親フォルダや隠しファイルは指定できません。")
        if parts[0] == "data" or Path(name).suffix.lower() not in EXTENSIONS:
            raise ValueError("編集できるコードファイルの種類を確認してください。dataはDB専用です。")
        if not isinstance(content, str) or "\x00" in content:
            raise ValueError("ファイルにはテキストを入力してください。")
        size = len(content.encode("utf-8"))
        if size > MAX_FILE_BYTES:
            raise ValueError("1ファイルは100KBまでです。")
        total += size
    if total > MAX_PROJECT_BYTES:
        raise ValueError("プロジェクトのコードは合計500KBまでです。")


class BuildStore:
    def __init__(self, instance_path):
        self.path = Path(instance_path) / "build.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, name TEXT NOT NULL,
                files TEXT NOT NULL, active_file TEXT NOT NULL,
                revision INTEGER NOT NULL DEFAULT 1,
                runtime_state TEXT NOT NULL DEFAULT '{}',
                runtime_secret TEXT NOT NULL, chat TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def list_projects(self, owner):
        with self.connect() as db:
            rows = db.execute("SELECT id, name FROM projects WHERE owner=? ORDER BY updated_at DESC, id", (owner,)).fetchall()
        return [dict(row) for row in rows]

    def create(self, owner, name):
        name = self.validate_name(name)
        project_id = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT COUNT(*) FROM projects WHERE owner=?", (owner,)).fetchone()[0] >= 10:
                raise ValueError("初期版ではプロジェクトは10個までです。")
            db.execute("""INSERT INTO projects
                (id, owner, name, files, active_file, runtime_secret) VALUES (?, ?, ?, ?, ?, ?)""",
                (project_id, owner, name, json.dumps(STARTER_FILES, ensure_ascii=False),
                 "templates/index.html", secrets.token_hex(32)))
        return self.get(owner, project_id)

    @staticmethod
    def validate_name(name):
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError("プロジェクト名は1〜80文字で入力してください。")
        return name.strip()

    def get(self, owner, project_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM projects WHERE id=? AND owner=?", (project_id, owner)).fetchone()
        if row is None:
            raise LookupError("プロジェクトが見つかりません。")
        project = dict(row)
        for key in ("files", "runtime_state", "chat"):
            project[key] = json.loads(project[key])
        return project

    def save(self, owner, project_id, data):
        files = data.get("files")
        validate_files(files)
        name = self.validate_name(data.get("name"))
        active_file = data.get("active_file")
        if not isinstance(active_file, str) or active_file not in files:
            raise ValueError("編集中のファイルを選択してください。")
        if type(data.get("revision")) is not int:
            raise ValueError("保存バージョンを確認してください。")
        with self.connect() as db:
            result = db.execute("""UPDATE projects SET name=?, files=?, active_file=?,
                revision=revision+1, updated_at=CURRENT_TIMESTAMP
                WHERE id=? AND owner=? AND revision=?""",
                (name, json.dumps(files, ensure_ascii=False), active_file,
                 project_id, owner, data.get("revision")))
            if result.rowcount != 1:
                raise FileExistsError("別の画面で保存されています。コードを控えてから再読み込みしてください。")
        return self.get(owner, project_id)

    def save_runtime(self, owner, project_id, revision, state):
        with self.connect() as db:
            result = db.execute("UPDATE projects SET runtime_state=? WHERE id=? AND owner=? AND revision=?",
                                (json.dumps(state), project_id, owner, revision))
            if result.rowcount != 1:
                raise FileExistsError("実行中にコードが更新されました。保存して再実行してください。")

    def save_chat(self, owner, project_id, history):
        with self.connect() as db:
            db.execute("UPDATE projects SET chat=? WHERE id=? AND owner=?",
                       (json.dumps(history[-20:], ensure_ascii=False), project_id, owner))


def public_project(project):
    return {key: project[key] for key in ("id", "name", "files", "active_file", "revision", "chat")}
