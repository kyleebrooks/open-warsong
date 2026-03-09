from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import hashlib
import json
from collections import Counter

from romkit import GenesisRom, _be16, _be32


@dataclass
class OpcodeHit:
    offset: int
    opcode: int
    target: int
    kind: str


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect_ascii_strings(data: bytes, min_len: int = 4) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    i = 0
    n = len(data)
    while i < n:
        if 0x20 <= data[i] <= 0x7E:
            start = i
            while i < n and 0x20 <= data[i] <= 0x7E:
                i += 1
            if i - start >= min_len:
                out.append((start, data[start:i].decode("ascii", errors="ignore")))
        else:
            i += 1
    return out


def scan_absolute_control_flow(data: bytes) -> list[OpcodeHit]:
    """Scan for common absolute jump/call forms:
    - JSR abs.l: 4E B9 xx xx xx xx
    - JMP abs.l: 4E F9 xx xx xx xx
    """
    out: list[OpcodeHit] = []
    i = 0
    n = len(data)
    while i + 5 < n:
        op = _be16(data, i)
        if op == 0x4EB9:
            target = _be32(data, i + 2)
            out.append(OpcodeHit(i, op, target, "jsr_abs_l"))
            i += 6
            continue
        if op == 0x4EF9:
            target = _be32(data, i + 2)
            out.append(OpcodeHit(i, op, target, "jmp_abs_l"))
            i += 6
            continue
        i += 2
    return out


def byte_frequency(data: bytes) -> dict[str, int]:
    c = Counter(data)
    return {f"0x{k:02X}": v for k, v in sorted(c.items())}


def write_control_flow_csv(path: Path, hits: list[OpcodeHit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["offset", "opcode", "kind", "target"])
        for h in hits:
            w.writerow([f"0x{h.offset:06X}", f"0x{h.opcode:04X}", h.kind, f"0x{h.target:08X}"])


def write_strings_csv(path: Path, strings: list[tuple[int, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["offset", "text"])
        for off, text in strings:
            w.writerow([f"0x{off:06X}", text])


def write_analysis_report(path: Path, rom: GenesisRom, strings: list[tuple[int, str]], hits: list[OpcodeHit]) -> None:
    header = rom.parse_header()
    report = {
        "rom": {
            "path": str(rom.path),
            "size": len(rom.data),
            "sha256": sha256_hex(rom.data),
            "header_checksum": f"0x{header.checksum:04X}",
            "computed_checksum": f"0x{rom.computed_checksum():04X}",
            "rom_start": f"0x{header.rom_start:08X}",
            "rom_end": f"0x{header.rom_end:08X}",
        },
        "stats": {
            "ascii_string_count": len(strings),
            "control_flow_hit_count": len(hits),
            "top_control_flow_targets": [
                {"target": f"0x{t:08X}", "count": c}
                for t, c in Counter(h.target for h in hits).most_common(32)
            ],
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
