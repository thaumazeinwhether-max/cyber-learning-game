"""実行方式の境界。PythonはDocker内だけで実行し、ローカルPythonへ代替しない。"""

import base64
import json
import os
import shutil
import subprocess
import threading
import uuid

IMAGE = "cyber-build-runtime:1"
OUTPUT_LIMIT = 3_000_000
STATE_LIMIT = 1_000_000


class RuntimeUnavailable(ValueError):
    pass


def docker_environment():
    # 外部デーモンを指定する環境変数を引き継がず、検査したローカル接続先を明示する。
    return {key: value for key, value in os.environ.items()
            if key.upper() not in {"DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"}}


def is_local_endpoint(endpoint):
    return isinstance(endpoint, str) and endpoint.startswith(("npipe:////./pipe/", "unix:///"))


def runtime_status(enabled):
    if not enabled or not shutil.which("docker"):
        return {"available": False, "message": "Flask実行環境が未設定です。HTML/CSSを確認し、Pythonは保存できます。"}
    try:
        environment = docker_environment()
        context = subprocess.run(["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"],
                                 capture_output=True, text=True, timeout=3, env=environment)
        endpoint = context.stdout.strip()
        if context.returncode != 0 or not is_local_endpoint(endpoint):
            return {"available": False, "message": "Flask実行にはローカルのDocker接続先が必要です。外部デーモンは使用しません。"}
        info = subprocess.run(["docker", "--host", endpoint, "info", "--format", "{{.OSType}}"],
                              capture_output=True, text=True, timeout=3, env=environment)
        image = subprocess.run(["docker", "--host", endpoint, "image", "inspect", IMAGE],
                               capture_output=True, timeout=3, env=environment)
        available = info.returncode == 0 and info.stdout.strip() == "linux" and image.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        available = False
    return {"available": available, "endpoint": endpoint if available else None,
            "message": "Flask隔離実行を利用できます。" if available else "LinuxコンテナーとBuild専用イメージを確認してください。"}


def container_command(name, endpoint):
    if not is_local_endpoint(endpoint):
        raise RuntimeUnavailable("ローカルのDocker接続先だけを利用できます。")
    return ["docker", "--host", endpoint, "run", "--rm", "--interactive", "--pull=never", "--name", name,
            "--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--user=65534:65534", "--memory=192m", "--memory-swap=192m", "--cpus=0.5",
            "--pids-limit=32", "--ulimit=nofile=128:128", "--log-driver=none",
            "--tmpfs=/workspace:rw,noexec,nosuid,size=16m,uid=65534,gid=65534,mode=700",
            "--tmpfs=/tmp:rw,noexec,nosuid,size=8m,uid=65534,gid=65534,mode=700", IMAGE]


def bounded_container_call(command, payload, timeout=10):
    """入力待ち・無限出力・無限ループでも、ホストが待ち続けないようにする。"""
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=docker_environment())
    output = bytearray()
    overflow = threading.Event()

    def write_input():
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except (OSError, ValueError):
            pass

    def read_output():
        while True:
            chunk = process.stdout.read(8192)
            if not chunk:
                break
            if len(output) + len(chunk) > OUTPUT_LIMIT:
                overflow.set()
                process.kill()
                break
            output.extend(chunk)

    writer = threading.Thread(target=write_input, daemon=True)
    reader = threading.Thread(target=read_output, daemon=True)
    writer.start()
    reader.start()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)
        raise ValueError("実行が10秒を超えました。ループやapp.run()の呼び出しを確認してください。") from None
    finally:
        reader.join(timeout=2)
        writer.join(timeout=2)
    if overflow.is_set():
        raise ValueError("実行結果が大きすぎます。大量の出力を減らしてください。")
    if process.returncode != 0:
        raise ValueError("隔離実行を終了しました。実行環境またはメモリ使用量を確認してください。")
    return bytes(output)


def validate_runtime_result(result):
    if not isinstance(result, dict):
        raise ValueError("実行結果の形式が不正です。")
    if not isinstance(result.get("html"), str) or len(result["html"]) > 300_000:
        raise ValueError("HTML出力の大きさを確認してください。")
    if type(result.get("status")) is not int or not 100 <= result["status"] <= 599:
        raise ValueError("HTTPステータスが不正です。")
    state = result.get("state", {})
    if not isinstance(state, dict) or set(state) - {"database", "cookie"}:
        raise ValueError("実行状態の形式が不正です。")
    encoded = state.get("database", "")
    cookie = state.get("cookie", "")
    if not isinstance(encoded, str) or len(encoded) > STATE_LIMIT * 2:
        raise ValueError("DBは1MBまでです。")
    try:
        database = base64.b64decode(encoded, validate=True)
    except ValueError:
        raise ValueError("DBの返却形式が不正です。") from None
    if len(database) > STATE_LIMIT:
        raise ValueError("DBは1MBまでです。")
    if not isinstance(cookie, str) or len(cookie) > 8000 or "\r" in cookie or "\n" in cookie:
        raise ValueError("アプリのSessionが大きすぎます。")
    logs = result.get("logs", "")
    if not isinstance(logs, str):
        raise ValueError("ログの形式が不正です。")
    return {"html": result["html"], "status": result["status"],
            "state": {"database": encoded, "cookie": cookie}, "logs": logs[-8000:]}


class DockerRuntime:
    def __init__(self, endpoint):
        if not is_local_endpoint(endpoint):
            raise RuntimeUnavailable("ローカルのDocker接続先だけを利用できます。")
        self.endpoint = endpoint

    def run(self, project, path, method, data):
        name = "cyber-build-" + uuid.uuid4().hex
        payload = json.dumps({"files": project["files"], "state": project["runtime_state"],
                              "secret": project["runtime_secret"], "path": path,
                              "method": method, "data": data}, ensure_ascii=False).encode("utf-8")
        try:
            raw = bounded_container_call(container_command(name, self.endpoint), payload)
            try:
                result = json.loads(raw)
            except (ValueError, UnicodeError):
                raise ValueError("実行結果を読み取れませんでした。プロセスの強制終了や直接出力を確認してください。") from None
            return validate_runtime_result(result)
        except OSError:
            raise RuntimeUnavailable("Dockerを起動し、Build実行環境を確認してください。") from None
        finally:
            # CLI側を停止してもコンテナーが残る場合があるため、名前を指定して後始末する。
            try:
                subprocess.run(["docker", "--host", self.endpoint, "rm", "--force", name], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=3, env=docker_environment())
            except (OSError, subprocess.TimeoutExpired):
                pass
