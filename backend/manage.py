#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
from pathlib import Path


def ensure_correct_python():
    """
    Ensure Django runs under Python 3.13 with PyTorch support.
    If invoked with Python 3.14 (system python where PyTorch DLL is blocked on Windows),
    automatically forward execution to backend/django/Scripts/python.exe.
    """
    if sys.version_info >= (3, 14):
        base_dir = Path(__file__).resolve().parent
        venv_py = base_dir / "django" / "Scripts" / "python.exe"
        if venv_py.exists():
            print(f"[BIU Traffic AI] Detected Python {sys.version.split()[0]} (PyTorch blocked by Windows).")
            print(f"[BIU Traffic AI] Switching automatically to Python 3.13 venv: {venv_py}")
            sys.exit(subprocess.call([str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:]))


def main():
    """Run administrative tasks."""
    ensure_correct_python()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
