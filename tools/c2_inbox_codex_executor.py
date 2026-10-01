"""Retired recursive Inbox executor. Use c3_runtime.py --inbox-only."""
def execute(*args, **kwargs):
    raise RuntimeError("retired_recursive_inbox_executor")
maintain = execute
if __name__ == "__main__":
    raise SystemExit("retired_recursive_inbox_executor: use c3_runtime.py --inbox-only")
