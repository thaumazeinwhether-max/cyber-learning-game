"""PID 1の監視役。準備完了後にだけ入力を受け、子の実行を10秒で止める。"""

import os
import signal
import sys

# -Iではスクリプトのフォルダも検索対象外。読み取り専用のイメージ内だけを追加する。
sys.path.insert(0, "/")
from runner import main

READY = "CYBER_BUILD_READY_V1\n"
EXECUTION_SECONDS = 10


class ExecutionTimeout(BaseException):
    pass


def deadline_reached(signum, frame):
    raise ExecutionTimeout()


def supervise():
    signal.signal(signal.SIGALRM, deadline_reached)
    # Flaskなど信頼済みのimportは済んでいる。まだ利用者のコードも入力も受け取っていない。
    sys.stdout.write(READY)
    sys.stdout.flush()
    signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        payload = sys.stdin.buffer.read(4_000_000)
    except ExecutionTimeout:
        return 125
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    child = os.fork()
    if child == 0:
        os.setsid()
        try:
            import json
            main(bundle=json.loads(payload))
            sys.stdout.flush()
            os._exit(0)
        except BaseException:
            os._exit(1)

    # 未信頼コードはこの親では実行しない。子が自身のsignal設定を変えても親の時計は変わらない。
    # このプロセスはPID 1。終了すると別プロセスを作った利用者コードもnamespaceごと終了する。
    signal.setitimer(signal.ITIMER_REAL, EXECUTION_SECONDS)
    try:
        _, status = os.waitpid(child, 0)
        return os.waitstatus_to_exitcode(status)
    except ExecutionTimeout:
        try:
            os.kill(child, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return 124
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    sys.exit(supervise())
