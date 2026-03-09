#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib

from open_warsong_path import ensure_import_path
ensure_import_path()
from romkit import GenesisRom


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify JSON->IPS and IPS->ROM workflow round-trip")
    ap.add_argument("--base-rom", required=True)
    ap.add_argument("--mod", required=True)
    ap.add_argument("--workdir", default="open/verify")
    args = ap.parse_args()

    root = Path(args.workdir)
    root.mkdir(parents=True, exist_ok=True)

    ips = root / "mod.ips"
    rom_from_json = root / "mod_from_json.md"
    rom_from_ips = root / "mod_from_ips.md"

    import subprocess

    subprocess.run([
        "python", "scripts/build_patch.py",
        "--rom", args.base_rom,
        "--mod", args.mod,
        "--out", str(ips),
        "--fix-checksum",
        "--out-rom", str(rom_from_json),
    ], check=True)

    base_sha = sha256_hex(Path(args.base_rom))

    subprocess.run([
        "python", "scripts/apply_patch.py",
        "--rom", args.base_rom,
        "--ips", str(ips),
        "--out-rom", str(rom_from_ips),
        "--expect-sha256", base_sha,
        "--fix-checksum",
    ], check=True)

    sha_json = sha256_hex(rom_from_json)
    sha_ips = sha256_hex(rom_from_ips)

    if sha_json != sha_ips:
        raise SystemExit(
            "Round-trip mismatch:\n"
            f"  JSON-built ROM: {sha_json}\n"
            f"  IPS-applied ROM: {sha_ips}"
        )

    meta = GenesisRom(rom_from_ips)
    print("Round-trip verification passed")
    print(f"Base ROM SHA-256:   {base_sha}")
    print(f"Patched ROM SHA-256:{sha_ips}")
    print(f"Patched checksum header/computed: 0x{meta.parse_header().checksum:04X} / 0x{meta.computed_checksum():04X}")


if __name__ == "__main__":
    main()
