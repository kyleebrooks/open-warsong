from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from romkit import _be16, _be32


@dataclass
class Instruction:
    addr: int
    size: int
    text: str
    flow_targets: list[int]
    terminal: bool = False


def _in_rom(addr: int, size: int, rom_len: int) -> bool:
    return 0 <= addr <= rom_len - size


def decode_instruction(data: bytes, addr: int) -> Instruction:
    if not _in_rom(addr, 2, len(data)):
        return Instruction(addr, 0, "; out-of-range", [], True)

    op = _be16(data, addr)

    if op == 0x4E75:
        return Instruction(addr, 2, "rts", [], True)
    if op == 0x4E71:
        return Instruction(addr, 2, "nop", [])
    if op == 0x4E56 and _in_rom(addr, 4, len(data)):
        imm = _be16(data, addr + 2)
        return Instruction(addr, 4, f"link a6,#${imm:04X}", [])
    if op == 0x4E5E:
        return Instruction(addr, 2, "unlk a6", [])

    if op == 0x4EB9 and _in_rom(addr, 6, len(data)):
        target = _be32(data, addr + 2)
        return Instruction(addr, 6, f"jsr loc_{target:06X}", [target])

    if op == 0x4EF9 and _in_rom(addr, 6, len(data)):
        target = _be32(data, addr + 2)
        return Instruction(addr, 6, f"jmp loc_{target:06X}", [target], True)

    # Bcc/BRA/BSR handling for 68000 short/word forms.
    if (op & 0xF000) == 0x6000:
        cond = (op >> 8) & 0xF
        disp8 = op & 0xFF
        mnemonic = ["bra", "bsr", "bhi", "bls", "bcc", "bcs", "bne", "beq", "bvc", "bvs", "bpl", "bmi", "bge", "blt", "bgt", "ble"][cond]

        if disp8 == 0 and _in_rom(addr, 4, len(data)):
            disp = _be16(data, addr + 2)
            if disp & 0x8000:
                disp -= 0x10000
            target = (addr + 2 + disp) & 0xFFFFFFFF
            terminal = mnemonic == "bra"
            return Instruction(addr, 4, f"{mnemonic}.w loc_{target:06X}", [target], terminal)

        if disp8 != 0xFF:
            disp = disp8 - 0x100 if disp8 & 0x80 else disp8
            target = (addr + 2 + disp) & 0xFFFFFFFF
            terminal = mnemonic == "bra"
            return Instruction(addr, 2, f"{mnemonic}.s loc_{target:06X}", [target], terminal)

    # Unknown instruction fallback (keep sweep deterministic).
    return Instruction(addr, 2, f"dc.w ${op:04X}", [])


def walk_code(data: bytes, entry_points: list[int], max_instructions: int = 40000) -> tuple[dict[int, Instruction], set[int]]:
    queue = [ep for ep in entry_points if 0 <= ep < len(data)]
    visited: dict[int, Instruction] = {}
    labels: set[int] = set(queue)

    while queue and len(visited) < max_instructions:
        addr = queue.pop(0)
        if addr in visited or not (0 <= addr < len(data)):
            continue

        cur = addr
        linear_budget = 512
        while linear_budget > 0 and cur not in visited and 0 <= cur < len(data) and len(visited) < max_instructions:
            ins = decode_instruction(data, cur)
            visited[cur] = ins

            for t in ins.flow_targets:
                if 0 <= t < len(data):
                    labels.add(t)
                    if t not in visited:
                        queue.append(t)

            if ins.size <= 0:
                break

            next_addr = cur + ins.size
            if ins.terminal:
                break

            if next_addr not in visited:
                queue.append(next_addr)
            cur = next_addr
            linear_budget -= 1

    return visited, labels


def render_asm(path: Path, visited: dict[int, Instruction], labels: set[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for addr in sorted(visited):
        if addr in labels:
            lines.append(f"loc_{addr:06X}:")
        lines.append(f"    {visited[addr].text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
