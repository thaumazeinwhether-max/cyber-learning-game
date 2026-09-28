"""Docker準備と未信頼コードの期限を分離し、各失敗時の停止を確認する。"""

import io
import json
import os
import subprocess
import time
import uuid

import pytest

from src import build_runtime as runtime
from src.arena_scenarios import SCENARIOS
from src.arena_targets import target_files


class InputPipe(io.BytesIO):
    def close(self):
        if not self.closed:
            self.written = self.getvalue()
        super().close()


class Process:
    def __init__(self, output, timeout=False):
        self.stdin = InputPipe()
        self.stdout = io.BytesIO(output)
        self.returncode = None
        self.timeout = timeout
        self.waits = []
        self.killed = False

    def wait(self, timeout):
        self.waits.append(timeout)
        if self.timeout and not self.killed:
            raise subprocess.TimeoutExpired('fixture', timeout)
        self.returncode = -1 if self.killed else 0
        return self.returncode

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -1


def test_preparation_longer_than_execution_budget_does_not_consume_it(monkeypatch):
    clock = [0]
    process = Process(runtime.READY + b'{"status":200}')
    class StartupPipe(io.BytesIO):
        def readline(self, size):
            clock[0] += 12  # 実時間を待たず、準備に12秒必要だった状況を再現する。
            return super().readline(size)
    process.stdout = StartupPipe(runtime.READY + b'{"status":200}')
    monkeypatch.setattr(runtime.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(runtime.subprocess, 'Popen', lambda *a, **k: process)
    timings = {}
    assert runtime.bounded_container_call(['fixture'], b'input', timings=timings) == b'{"status":200}'
    assert timings['start_to_ready'] == 12
    assert process.waits == [10]
    assert process.stdin.written == b'input'


def test_bad_ready_never_sends_user_code(monkeypatch):
    process = Process(b'OLD_OR_BROKEN_RUNNER\n')
    monkeypatch.setattr(runtime.subprocess, 'Popen', lambda *a, **k: process)
    with pytest.raises(runtime.RuntimeUnavailable, match='準備通知'):
        runtime.bounded_container_call(['fixture'], b'untrusted-code')
    assert process.stdin.written == b''
    assert process.killed


def test_no_ready_times_out_without_sending_code(monkeypatch):
    process = Process(runtime.READY)
    monkeypatch.setattr(runtime.subprocess, 'Popen', lambda *a, **k: process)
    original_event = runtime.threading.Event
    class NotReady(original_event):
        def wait(self, timeout=None):
            if timeout == 30:
                return False
            return super().wait(timeout)
    monkeypatch.setattr(runtime.threading, 'Event', NotReady)
    with pytest.raises(runtime.RuntimeUnavailable, match='準備が30秒'):
        runtime.bounded_container_call(['fixture'], b'untrusted-code')
    assert process.stdin.written == b''
    assert process.killed


def test_execution_timeout_does_not_retry_or_accept_fake_ready(monkeypatch):
    process = Process(runtime.READY + runtime.READY, timeout=True)
    launches = []
    def launch(*args, **kwargs):
        launches.append(args)
        return process
    monkeypatch.setattr(runtime.subprocess, 'Popen', launch)
    with pytest.raises(ValueError, match='実行が10秒'):
        runtime.bounded_container_call(['fixture'], b'input')
    assert len(launches) == 1
    assert 9 < process.waits[0] <= 10
    assert process.killed


def test_output_limit_still_stops_process(monkeypatch):
    process = Process(runtime.READY + b'x' * (runtime.OUTPUT_LIMIT + 1))
    monkeypatch.setattr(runtime.subprocess, 'Popen', lambda *a, **k: process)
    with pytest.raises(ValueError, match='大きすぎ'):
        runtime.bounded_container_call(['fixture'], b'input')
    assert process.killed


def test_status_uses_preparation_budget_and_checks_protocol(monkeypatch):
    calls = []
    replies = [b'unix:///var/run/docker.sock\n', b'linux\n', b'ready-v1\n']
    def run(command, **kwargs):
        calls.append((command, kwargs))
        output = replies.pop(0)
        return subprocess.CompletedProcess(command, 0, output.decode() if kwargs.get('text') else output)
    monkeypatch.setattr(runtime.shutil, 'which', lambda name: '/docker')
    monkeypatch.setattr(runtime.subprocess, 'run', run)
    assert runtime.runtime_status(True)['available']
    assert len(calls) == 3
    assert all(options['timeout'] == 30 for _, options in calls)
    assert all(options['stdin'] == subprocess.DEVNULL for _, options in calls)
    assert 'pull' not in str(calls)


def test_create_timeout_still_cleans_up_without_starting(monkeypatch):
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        if command[3] == 'create':
            raise subprocess.TimeoutExpired(command, 30)
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(runtime.subprocess, 'run', run)
    with pytest.raises(runtime.RuntimeUnavailable, match='作成が30秒'):
        runtime.DockerRuntime('unix:///var/run/docker.sock').run(
            {'files': {}, 'runtime_state': {}, 'runtime_secret': 'test'}, '/', 'GET', {})
    assert [command[3] for command in calls] == ['create', 'rm']


actual_docker = pytest.mark.skipif(os.environ.get('ARENA_DOCKER_TESTS') != '1',
                                 reason='Explicit local Docker integration run only')


@actual_docker
@pytest.mark.parametrize('iteration', range(3))
def test_actual_docker_easy_records_repeated(iteration):
    status = runtime.runtime_status(True)
    assert status['available'], status
    runner = runtime.DockerRuntime(status['endpoint'])
    project = {'files': target_files(SCENARIOS['easy-records'], 'LAB-repeated'),
               'runtime_state': {}, 'runtime_secret': 'test-only'}
    public = runner.run(project, '/', 'GET', {})
    assert public['status'] == 200 and 'LAB-repeated' not in public['html']
    project['runtime_state'] = public['state']
    private = runner.run(project, '/records', 'GET', {'id': '102'})
    assert private['status'] == 200 and 'LAB-repeated' in private['html']
    print('warm', iteration, runner.last_timings)


@actual_docker
@pytest.mark.parametrize('location', ['import', 'request'])
def test_actual_docker_infinite_code_times_out_and_is_removed(location, monkeypatch):
    status = runtime.runtime_status(True)
    assert status['available'], status
    name_id = uuid.uuid4()
    monkeypatch.setattr(runtime.uuid, 'uuid4', lambda: name_id)
    code = 'import signal\nsignal.signal(signal.SIGALRM, signal.SIG_IGN)\nwhile True: pass\n'
    if location == 'request':
        code = 'from flask import Flask\napp=Flask(__name__)\n@app.get("/")\ndef index():\n    while True: pass\n'
    runner = runtime.DockerRuntime(status['endpoint'])
    with pytest.raises(ValueError, match='実行が10秒'):
        runner.run({'files': {'app.py': code}, 'runtime_state': {}, 'runtime_secret': 'test-only'}, '/', 'GET', {})
    assert 9 <= runner.last_timings['execution_and_result'] < 12
    inspect = subprocess.run(['docker', '--host', status['endpoint'], 'inspect', 'cyber-build-' + name_id.hex],
                             stdin=subprocess.DEVNULL, capture_output=True, timeout=30, env=runtime.docker_environment())
    assert inspect.returncode != 0
    print('timeout', location, runner.last_timings)


@actual_docker
def test_actual_docker_supervisor_enforces_deadline_independently():
    """ホストの10秒停止がなくても、製品と同じPID 1監視役が子の無限ループを止める。"""
    status = runtime.runtime_status(True)
    assert status['available'], status
    name = 'cyber-build-watchdog-' + uuid.uuid4().hex
    base = ['docker', '--host', status['endpoint']]
    environment = runtime.docker_environment()
    command = runtime.container_command(name, status['endpoint'])
    payload = json.dumps({'files': {'app.py': 'import signal\nsignal.signal(signal.SIGALRM, signal.SIG_IGN)\nwhile True: pass'},
                          'state': {}, 'secret': 'test-only', 'path': '/', 'method': 'GET', 'data': {}}).encode()
    try:
        subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, env=environment, timeout=30, check=True)
        process = subprocess.Popen(base + ['start', '--attach', '--interactive', name],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment)
        started = time.monotonic()
        try:
            output, _ = process.communicate(payload, timeout=20)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
        assert output.startswith(runtime.READY)
        assert process.returncode == 124
        assert 10 <= time.monotonic() - started < 20
        inspect = subprocess.run(base + ['inspect', name], stdin=subprocess.DEVNULL,
                                 capture_output=True, env=environment, timeout=30)
        assert inspect.returncode != 0  # --rmで自動削除されている。
    finally:
        subprocess.run(base + ['rm', '--force', name], stdin=subprocess.DEVNULL,
                       capture_output=True, env=environment, timeout=30)
