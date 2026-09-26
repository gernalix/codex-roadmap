"""Small bounded CDP client for preparing one successor ChatGPT session.

The existing Playwright browser controller can hang during its CDP handshake on
this host. This client uses the same authenticated Chrome endpoint directly and
never reads conversation contents.
"""
from __future__ import annotations

import json
import time
from urllib.request import urlopen

ENDPOINT = 'http://127.0.0.1:9333'


class BrowserRecoveryError(RuntimeError):
    pass


class CDP:
    def __init__(self, url):
        try:
            import websocket
        except ImportError as exc:
            raise BrowserRecoveryError('python_websocket_client_missing') from exc
        self.socket = websocket.create_connection(url, timeout=5, suppress_origin=True)
        self.sequence = 0

    def call(self, method, params=None):
        self.sequence += 1
        call_id = self.sequence
        self.socket.send(json.dumps({'id': call_id, 'method': method, 'params': params or {}}))
        while True:
            response = json.loads(self.socket.recv())
            if response.get('id') != call_id:
                continue
            if 'error' in response:
                raise BrowserRecoveryError('cdp_rejected:' + method)
            return response.get('result', {})

    def close(self):
        self.socket.close()


def _json(path):
    with urlopen(ENDPOINT + path, timeout=5) as stream:
        return json.load(stream)


def _evaluate(page, expression):
    result = page.call('Runtime.evaluate', {'expression': expression, 'returnByValue': True})
    if result.get('exceptionDetails'):
        raise BrowserRecoveryError('browser_evaluation_failed')
    return result.get('result', {}).get('value')


def open_successor_tab():
    version = _json('/json/version')
    browser = CDP(version['webSocketDebuggerUrl'])
    try:
        target = browser.call('Target.createTarget', {'url': 'https://chatgpt.com/'})['targetId']
    finally:
        browser.close()
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        matches = [p for p in _json('/json/list') if p.get('id') == target]
        if matches and matches[0].get('webSocketDebuggerUrl'):
            return target, CDP(matches[0]['webSocketDebuggerUrl'])
        time.sleep(0.25)
    raise BrowserRecoveryError('successor_tab_unavailable')


def send_recovery_message(page, message):
    deadline = time.monotonic() + 30
    selector = '[contenteditable="true"][role="textbox"]'
    while time.monotonic() < deadline:
        present = _evaluate(page, '!!document.querySelector(' + json.dumps(selector) + ')')
        if present:
            break
        time.sleep(0.5)
    else:
        raise BrowserRecoveryError('composer_unavailable')
    _evaluate(page, 'document.querySelector(' + json.dumps(selector) + ').focus()')
    page.call('Input.insertText', {'text': message})
    populated = _evaluate(page, 'document.querySelector(' + json.dumps(selector) + ').innerText.length')
    if populated < len(message) // 2:
        raise BrowserRecoveryError('composer_fill_unconfirmed')
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if _evaluate(page, '!!document.querySelector("button[aria-label=Send]:not([disabled])")'):
            break
        time.sleep(0.25)
    else:
        raise BrowserRecoveryError('send_button_unavailable')
    _evaluate(page, 'document.querySelector("button[aria-label=Send]").click()')
    deadline = time.monotonic() + 75
    while time.monotonic() < deadline:
        url = _evaluate(page, 'location.href')
        if isinstance(url, str) and '/c/' in url and '/c/WEB:' not in url:
            return url
        time.sleep(0.5)
    raise BrowserRecoveryError('successor_session_unconfirmed')


def existing_session(target):
    match = next((p for p in _json('/json/list') if p.get('id') == target), None)
    if not match or not match.get('webSocketDebuggerUrl'):
        return None
    page = CDP(match['webSocketDebuggerUrl'])
    try:
        url = _evaluate(page, 'location.href')
        return url if isinstance(url, str) and '/c/' in url and '/c/WEB:' not in url else None
    finally:
        page.close()
