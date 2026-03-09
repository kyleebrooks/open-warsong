#!/usr/bin/env python3
from pathlib import Path
import argparse
import json

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import GenesisRom
from analysis import scan_absolute_control_flow
from disasm import walk_code, render_asm


def main() -> None:
    ap = argparse.ArgumentParser(description="Run a control-flow aware 68k disassembly pass")
    ap.add_argument("--rom", required=True)
    ap.add_argument("--out", default="open/disasm")
    ap.add_argument("--max-insn", type=int, default=40000)
    args = ap.parse_args()

    rom = GenesisRom(Path(args.rom))
    vectors = [v for v in rom.read_vectors() if 0 <= v < len(rom.data)]
    abs_targets = [h.target for h in scan_absolute_control_flow(rom.data) if 0 <= h.target < len(rom.data)]

    entry_points = sorted(set(vectors + abs_targets))
    visited, labels = walk_code(rom.data, entry_points, max_instructions=args.max_insn)

    out = Path(args.out)
    render_asm(out / "code_pass1.asm", visited, labels)

    summary = {
        "entry_points": len(entry_points),
        "decoded_instructions": len(visited),
        "labels": len(labels),
        "max_instructions": args.max_insn,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Disassembly pass complete: {out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
