"""One clean, pinned source path for C2's ChatGPT browser safety layer."""
from pathlib import Path


SUPERVISOR_SRC = Path.home() / '.local/share/chatgpt-rdc-supervisor/source/src'


def require_supervisor_source() -> Path:
    if not (SUPERVISOR_SRC / 'chatgpt_rdc_supervisor/safety.py').is_file():
        raise RuntimeError('supervisor_safety_runtime_missing')
    return SUPERVISOR_SRC
