#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import apply_ips, with_updated_header_checksum, compute_genesis_checksum, GenesisRom


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply an IPS patch to a ROM and optionally repair checksum")
    ap.add_argument("--rom", required=True, help="Source ROM")
    ap.add_argument("--ips", required=True, help="IPS patch path")
    ap.add_argument("--out-rom", required=True, help="Output patched ROM path")
    ap.add_argument("--expect-sha256", help="Optional source ROM SHA-256 guard")
    ap.add_argument("--fix-checksum", action="store_true", help="Recompute ROM header checksum after applying patch")
    args = ap.parse_args()

    rom_path = Path(args.rom)
    ips_path = Path(args.ips)
    out_path = Path(args.out_rom)

    source = rom_path.read_bytes()
    if args.expect_sha256:
        got = sha256_hex(source)
        if got.lower() != args.expect_sha256.lower():
            raise SystemExit(
                f"Source ROM SHA-256 mismatch:\n  expected={args.expect_sha256.lower()}\n  got={got.lower()}"
            )

    patched = apply_ips(source, ips_path.read_bytes())
    if args.fix_checksum:
        patched = with_updated_header_checksum(patched)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(patched)

    src_meta = GenesisRom(rom_path)
    dst_meta = GenesisRom(out_path)

    print(f"Applied patch: {ips_path}")
    print(f"Wrote ROM: {out_path}")
    print(f"Source SHA-256:  {sha256_hex(source)}")
    print(f"Patched SHA-256: {sha256_hex(patched)}")
    print(f"Source checksum(header/computed): 0x{src_meta.parse_header().checksum:04X} / 0x{src_meta.computed_checksum():04X}")
    print(f"Patched checksum(header/computed): 0x{dst_meta.parse_header().checksum:04X} / 0x{dst_meta.computed_checksum():04X}")
    if compute_genesis_checksum(patched) == dst_meta.parse_header().checksum:
        print("Patched ROM checksum is consistent.")


if __name__ == "__main__":
    main()
