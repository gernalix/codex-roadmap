"""Disposable HTTP fixture for real-browser loading/error/empty-state smoke.
Run after node web/build.mjs; set the mode file to empty/error.
This does not read or write operational roadmap data.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c3_api import serve


class Fixture:
    def __init__(self, mode):
        self.mode = mode

    def state(self):
        if self.mode.read_text().strip() == 'error':
            raise RuntimeError('Smoke fixture: canonical source unavailable')
        return {'items': [], 'dependencies': [], 'events': [], 'authority': 'disposable-browser-fixture'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode-file', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8769)
    args = parser.parse_args()
    serve(Fixture(args.mode_file), args.port).serve_forever()
