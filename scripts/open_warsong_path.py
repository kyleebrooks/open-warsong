#!/usr/bin/env python3
from pathlib import Path
import sys


def ensure_import_path() -> None:
    root = Path(__file__).resolve().parent.parent
    pkg = root / "open-warsong"
    if str(pkg) not in sys.path:
        sys.path.insert(0, str(pkg))
