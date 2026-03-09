#!/usr/bin/env python3
from pathlib import Path
import argparse
import json

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import GenesisRom, apply_byte_patches, write_ips, with_updated_header_checksum


def main() -> None:
    ap = argparse.ArgumentParser(description="Build IPS patch from JSON byte edits")
    ap.add_argument("--rom", required=True)
    ap.add_argument("--mod", required=True, help="JSON file with {'patches': [{'offset':'0x1234','bytes':'AA BB','expect':'11 22'}]}")
    ap.add_argument("--out", required=True, help="Output IPS path")
    ap.add_argument("--out-rom", help="Optional output modified ROM path")
    ap.add_argument("--fix-checksum", action="store_true", help="Recompute and update ROM header checksum after edits")
    args = ap.parse_args()

    rom = GenesisRom(Path(args.rom))
    spec = json.loads(Path(args.mod).read_text(encoding="utf-8"))
    modified = apply_byte_patches(rom.data, spec["patches"], strict=True)

    if args.fix_checksum:
        modified = with_updated_header_checksum(modified)

    write_ips(rom.data, modified, Path(args.out))

    if args.out_rom:
        out_rom = Path(args.out_rom)
        out_rom.parent.mkdir(parents=True, exist_ok=True)
        out_rom.write_bytes(modified)

    print(f"Wrote patch: {args.out}")
    if args.out_rom:
        print(f"Wrote modified ROM: {args.out_rom}")


if __name__ == "__main__":
    main()
