"""Bounded JSON-RPC MCP stdio client for real integration evidence."""
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


class MCPError(RuntimeError):
    pass


class MCPClient:
    def __init__(self, command, cwd, log, env=None, timeout=30):
        self.timeout = timeout
        self.buffer = b''
        self.counter = 0
        self.messages = []
        self.project_uri = Path(cwd).resolve().as_uri()
        self.log_path = Path(log)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log = open(self.log_path, 'wb')
        os.chmod(self.log_path, 0o600)
        child_env = dict(os.environ if env is None else env, PWD=str(Path(cwd).resolve()))
        self.process = subprocess.Popen(command, cwd=cwd, env=child_env, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=self.log, start_new_session=True)
        os.set_blocking(self.process.stdout.fileno(), False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def send(self, method, params, request_id=None):
        message = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if request_id is not None:
            message['id'] = request_id
        self.process.stdin.write((json.dumps(message) + '\n').encode())
        self.process.stdin.flush()

    def request(self, method, params=None):
        self.counter += 1
        request_id = self.counter
        self.send(method, params or {}, request_id)
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                if not line.strip():
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as error:
                    raise MCPError('Non-JSON protocol output; inspect local server log') from error
                self.messages.append(message)
                self.messages = self.messages[-256:]
                if 'method' in message and 'id' in message:
                    response = {'jsonrpc': '2.0', 'id': message['id']}
                    if message['method'] == 'roots/list':
                        response['result'] = {'roots': [{'uri': self.project_uri, 'name': 'current project'}]}
                    elif message['method'] == 'ping':
                        response['result'] = {}
                    else:
                        response['error'] = {'code': -32601, 'message': 'Unsupported client method'}
                    self.process.stdin.write((json.dumps(response) + '\n').encode())
                    self.process.stdin.flush()
                    continue
                if message.get('id') != request_id:
                    continue
                if 'error' in message:
                    raise MCPError('MCP method failed: ' + method + ' ' + json.dumps(message['error']))
                return message['result']
            if self.process.poll() is not None:
                # Drain already-written responses before reporting a terminal server.
                try:
                    chunk = os.read(self.process.stdout.fileno(), 65536)
                except BlockingIOError:
                    chunk = b''
                if chunk:
                    self.buffer += chunk
                    continue
                raise MCPError('MCP process exited: ' + str(self.process.returncode))
            if self.selector.select(min(1, max(0, deadline - time.monotonic()))):
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if chunk:
                    self.buffer += chunk
        raise MCPError('MCP request timed out: ' + method + '; write outcome may be unknown')

    def initialize(self, project):
        result = self.request('initialize', {
            'protocolVersion': '2025-03-26', 'capabilities': {'roots': {'listChanged': False}},
            'clientInfo': {'name': 'personal-trellis-evidence', 'version': '1.0.0'},
            'rootUri': Path(project).as_uri()})
        self.send('notifications/initialized', {})
        return result

    def tools(self):
        result, cursor = [], None
        for _ in range(20):
            page = self.request('tools/list', {'cursor': cursor} if cursor else {})
            result.extend(page['tools'])
            cursor = page.get('nextCursor')
            if not cursor:
                return result
        raise MCPError('Tool catalog exceeded bounded pagination')

    def call(self, name, arguments=None):
        result = self.request('tools/call', {'name': name, 'arguments': arguments or {}})
        if result.get('isError'):
            raise MCPError('Tool returned an error: ' + name + ' ' + json.dumps(result.get('content', [])))
        return result

    def close(self):
        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
        # A launcher can exit before its server child. An inherited pipe reaches
        # EOF only when those writers also exit; avoid signalling an empty/reaped
        # group, while bounding a server child that ignores graceful termination.
        deadline = time.monotonic()+3
        eof = False
        while time.monotonic()<deadline:
            try:
                chunk = os.read(self.process.stdout.fileno(),65536)
            except BlockingIOError:
                self.selector.select(.05)
                continue
            if not chunk:
                eof = True
                break
        if not eof or self.process.poll() is None:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if self.process.poll() is None:
            self.process.wait(timeout=3)
        self.selector.close()
        self.process.stdin.close()
        self.process.stdout.close()
        self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
