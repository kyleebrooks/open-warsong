#!/usr/bin/env python3
from pathlib import Path
import argparse

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import GenesisRom, write_manifest, write_symbols_csv, write_vector_asm
from analysis import write_analysis_report, write_control_flow_csv, write_strings_csv, collect_ascii_strings, scan_absolute_control_flow
from disasm import walk_code, render_asm


def main() -> None:
    ap = argparse.ArgumentParser(description="Bootstrap an open reverse-engineering workspace from a Genesis ROM")
    ap.add_argument("--rom", required=True, help="Path to the ROM file")
    ap.add_argument("--out", default="open", help="Output directory")
    args = ap.parse_args()

    rom = GenesisRom(Path(args.rom))
    header = rom.parse_header()
    checksum = rom.computed_checksum()
    vectors = rom.read_vectors()

    out_dir = Path(args.out)
    chunks = rom.write_chunks(out_dir / "chunks")
    write_symbols_csv(out_dir / "symbols.csv", vectors)
    write_vector_asm(out_dir / "vectors_68k.asm", vectors)
    write_manifest(out_dir / "manifest.json", header, checksum, chunks)

    # First-pass static analysis artifacts for RE workflow
    strings = collect_ascii_strings(rom.data, min_len=5)
    hits = scan_absolute_control_flow(rom.data)
    write_strings_csv(out_dir / "analysis" / "ascii_strings.csv", strings)
    write_control_flow_csv(out_dir / "analysis" / "control_flow_abs.csv", hits)
    write_analysis_report(out_dir / "analysis" / "report.json", rom, strings, hits)

    # First pass disassembly from vectors + absolute flow targets
    entry_points = sorted({v for v in vectors if 0 <= v < len(rom.data)} | {h.target for h in hits if 0 <= h.target < len(rom.data)})
    visited, labels = walk_code(rom.data, entry_points, max_instructions=40000)
    render_asm(out_dir / "disasm" / "code_pass1.asm", visited, labels)

    print(f"Bootstrapped workspace in {out_dir}")
    print(f"Header checksum:  0x{header.checksum:04X}")
    print(f"Computed checksum: 0x{checksum:04X}")


if __name__ == "__main__":
    main()
