"""Phase 3専用DB。Buildのprojectsへは書き込まない。"""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class ArenaStore:
    def __init__(self, instance_path):
        self.path = Path(instance_path) / "arena.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS arena_sessions (owner TEXT PRIMARY KEY, state TEXT NOT NULL)")

    @contextmanager
    def edit(self, owner):
        # 同一挑戦への二重操作・別タブをSQLiteトランザクションで直列化する。
        with sqlite3.connect(self.path, timeout=1) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state FROM arena_sessions WHERE owner=?", (owner,)).fetchone()
            state = json.loads(row[0]) if row else {"difficulty": "easy", "targets": [], "attack": None,
                                                  "defend": None, "history": [], "view": ""}
            yield state
            db.execute("INSERT OR REPLACE INTO arena_sessions VALUES (?, ?)", (owner, json.dumps(state, ensure_ascii=False)))
