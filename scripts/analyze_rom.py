#!/usr/bin/env python3
from pathlib import Path
import argparse

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import GenesisRom
from analysis import (
    collect_ascii_strings,
    scan_absolute_control_flow,
    write_analysis_report,
    write_control_flow_csv,
    write_strings_csv,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run static analysis passes over Genesis ROM")
    ap.add_argument("--rom", required=True)
    ap.add_argument("--out", default="open/analysis")
    ap.add_argument("--min-string", type=int, default=5)
    args = ap.parse_args()

    rom = GenesisRom(Path(args.rom))
    out = Path(args.out)

    strings = collect_ascii_strings(rom.data, min_len=args.min_string)
    hits = scan_absolute_control_flow(rom.data)

    write_strings_csv(out / "ascii_strings.csv", strings)
    write_control_flow_csv(out / "control_flow_abs.csv", hits)
    write_analysis_report(out / "report.json", rom, strings, hits)

    print(f"Analysis complete: {out}")
    print(f"ASCII strings: {len(strings)}")
    print(f"Absolute JSR/JMP hits: {len(hits)}")


if __name__ == "__main__":
    main()
