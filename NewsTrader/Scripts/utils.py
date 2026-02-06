"""Utilities: Tee for dual logging, signal handler for graceful shutdown."""
import os


class Tee:
    """Write to multiple file-like objects (e.g. stdout and log file)."""

    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


def handle_sigint(sig, frame):
    """Graceful shutdown on Ctrl+C without messy tracebacks."""
    print("\n\nAborted by user (Ctrl+C)...")
    os._exit(0)
