#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate local Warsong ROM presence")
    ap.add_argument('--rom', default='Warsong (USA).md')
    args = ap.parse_args()

    p = Path(args.rom)
    if not p.exists():
        raise SystemExit(f"ROM not found: {p}")

    print(f"ROM path: {p}")
    print(f"ROM size: {p.stat().st_size}")
    print(f"SHA-256: {sha256_hex(p)}")


if __name__ == '__main__':
    main()
