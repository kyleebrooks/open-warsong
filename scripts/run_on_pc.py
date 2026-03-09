#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import subprocess

EMULATORS = [
    ("retroarch", ["-L", "genesis_plus_gx_libretro.so"]),
    ("blastem", []),
    ("genesis-plus-gx", []),
    ("kega-fusion", []),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Launch ROM on available PC emulator")
    ap.add_argument("--rom", required=True)
    args = ap.parse_args()

    rom = str(Path(args.rom).resolve())
    for exe, prefix in EMULATORS:
        path = shutil.which(exe)
        if path:
            cmd = [path, *prefix, rom]
            print("Launching:", " ".join(cmd))
            subprocess.run(cmd, check=False)
            return

    print("No known emulator found in PATH. Install one of:")
    for exe, _ in EMULATORS:
        print(f"  - {exe}")


if __name__ == "__main__":
    main()
