from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from romkit import _be16, _be32


# DBcc condition mnemonic lookup indexed by condition field.
DBCC_MNEMONICS = (
    "dbt", "dbra", "dbhi", "dbls", "dbcc", "dbcs", "dbne", "dbeq",
    "dbvc", "dbvs", "dbpl", "dbmi", "dbge", "dblt", "dbgt", "dble",
)


def _signed_word(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


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

    # MOVE immediate to data register.
    if (op & 0xF1FF) == 0x303C and _in_rom(addr, 4, len(data)):
        reg = (op >> 9) & 0x7
        imm = _be16(data, addr + 2)
        return Instruction(addr, 4, f"move.w #${imm:04X},d{reg}", [])
    if (op & 0xF1FF) == 0x203C and _in_rom(addr, 6, len(data)):
        reg = (op >> 9) & 0x7
        imm = _be32(data, addr + 2)
        return Instruction(addr, 6, f"move.l #${imm:08X},d{reg}", [])

    # MOVE address-register indirect to data register.
    if (op & 0xF1F8) == 0x3010:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"move.w (a{src}),d{dst}", [])
    if (op & 0xF1F8) == 0x2010:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"move.l (a{src}),d{dst}", [])

    # MOVE post-increment address-register indirect to data register.
    if (op & 0xF1F8) == 0x3018:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"move.w (a{src})+,d{dst}", [])
    if (op & 0xF1F8) == 0x2018:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"move.l (a{src})+,d{dst}", [])

    # MOVE displacement address-register indirect to data register.
    if (op & 0xF1F8) == 0x3028 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"move.w ({disp},a{src}),d{dst}", [])
    if (op & 0xF1F8) == 0x2028 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"move.l ({disp},a{src}),d{dst}", [])

    # MOVEQ #imm,Dn
    if (op & 0xF100) == 0x7000:
        reg = (op >> 9) & 0x7
        imm8 = op & 0xFF
        imm = imm8 - 0x100 if imm8 & 0x80 else imm8
        return Instruction(addr, 2, f"moveq #{imm},d{reg}", [])

    # ADDQ/SUBQ <ea> (subset: Dn direct)
    if (op & 0xF000) == 0x5000 and (op & 0x0038) == 0x0000:
        val = (op >> 9) & 0x7
        val = 8 if val == 0 else val
        size_bits = (op >> 6) & 0x3
        sz = {0: 'b', 1: 'w', 2: 'l'}.get(size_bits)
        if sz is not None:
            reg = op & 0x7
            mn = "subq" if (op & 0x0100) else "addq"
            return Instruction(addr, 2, f"{mn}.{sz} #{val},d{reg}", [])

    # CLR/TST Dn direct.
    if (op & 0xFF38) == 0x4200:
        size_bits = (op >> 6) & 0x3
        sz = {0: 'b', 1: 'w', 2: 'l'}.get(size_bits)
        if sz is not None:
            reg = op & 0x7
            return Instruction(addr, 2, f"clr.{sz} d{reg}", [])
    if (op & 0xFF38) == 0x4A00:
        size_bits = (op >> 6) & 0x3
        sz = {0: 'b', 1: 'w', 2: 'l'}.get(size_bits)
        if sz is not None:
            reg = op & 0x7
            return Instruction(addr, 2, f"tst.{sz} d{reg}", [])

    # CMPI #imm,Dn direct.
    if (op & 0xFF38) == 0x0C00:
        size_bits = (op >> 6) & 0x3
        reg = op & 0x7
        if size_bits == 0 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2) & 0x00FF
            return Instruction(addr, 4, f"cmpi.b #${imm:02X},d{reg}", [])
        if size_bits == 1 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2)
            return Instruction(addr, 4, f"cmpi.w #${imm:04X},d{reg}", [])
        if size_bits == 2 and _in_rom(addr, 6, len(data)):
            imm = _be32(data, addr + 2)
            return Instruction(addr, 6, f"cmpi.l #${imm:08X},d{reg}", [])

    # DBcc Dn,<disp16>
    if (op & 0xF0F8) == 0x50C8 and _in_rom(addr, 4, len(data)):
        cond = (op >> 8) & 0xF
        reg = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        target = (addr + 4 + disp) & 0xFFFFFFFF
        mnemonic = DBCC_MNEMONICS[cond]
        return Instruction(addr, 4, f"{mnemonic} d{reg},loc_{target:06X}", [target])
    # CMP (An)/(An)+,Dn subset.
    if (op & 0xF1F8) == 0xB050:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"cmp.w (a{src}),d{dst}", [])
    if (op & 0xF1F8) == 0xB090:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"cmp.l (a{src}),d{dst}", [])
    if (op & 0xF1F8) == 0xB058:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"cmp.w (a{src})+,d{dst}", [])
    if (op & 0xF1F8) == 0xB098:
        dst = (op >> 9) & 0x7
        src = op & 0x7
        return Instruction(addr, 2, f"cmp.l (a{src})+,d{dst}", [])
    if (op & 0xF1F8) == 0xB0A8 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"cmp.l ({disp},a{src}),d{dst}", [])
    if (op & 0xF1F8) == 0xB068 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"cmp.w ({disp},a{src}),d{dst}", [])

    if op == 0x4E56 and _in_rom(addr, 4, len(data)):
        imm = _be16(data, addr + 2)
        return Instruction(addr, 4, f"link a6,#${imm:04X}", [])
    if op == 0x4E5E:
        return Instruction(addr, 2, "unlk a6", [])

    if op == 0x4EB9 and _in_rom(addr, 6, len(data)):
        target = _be32(data, addr + 2)
        return Instruction(addr, 6, f"jsr loc_{target:06X}", [target])
    if op == 0x4EB8 and _in_rom(addr, 4, len(data)):
        target = _be16(data, addr + 2)
        return Instruction(addr, 4, f"jsr loc_{target:06X}", [target])

    if op == 0x4EF9 and _in_rom(addr, 6, len(data)):
        target = _be32(data, addr + 2)
        return Instruction(addr, 6, f"jmp loc_{target:06X}", [target], True)
    if op == 0x4EF8 and _in_rom(addr, 4, len(data)):
        target = _be16(data, addr + 2)
        return Instruction(addr, 4, f"jmp loc_{target:06X}", [target], True)

    # LEA absolute forms.
    if (op & 0xF1FF) == 0x41F9 and _in_rom(addr, 6, len(data)):
        reg = (op >> 9) & 0x7
        ea = _be32(data, addr + 2)
        return Instruction(addr, 6, f"lea loc_{ea:06X},a{reg}", [])
    if (op & 0xF1FF) == 0x41F8 and _in_rom(addr, 4, len(data)):
        reg = (op >> 9) & 0x7
        ea = _be16(data, addr + 2)
        return Instruction(addr, 4, f"lea loc_{ea:06X},a{reg}", [])

    # MOVEA immediate forms.
    if (op & 0xF1FF) == 0x307C and _in_rom(addr, 4, len(data)):
        reg = (op >> 9) & 0x7
        imm = _be16(data, addr + 2)
        return Instruction(addr, 4, f"movea.w #${imm:04X},a{reg}", [])
    if (op & 0xF1FF) == 0x207C and _in_rom(addr, 6, len(data)):
        reg = (op >> 9) & 0x7
        imm = _be32(data, addr + 2)
        return Instruction(addr, 6, f"movea.l #${imm:08X},a{reg}", [])

    # Bcc/BRA/BSR handling for 68000 short/word forms.
    if (op & 0xF000) == 0x6000:
        cond = (op >> 8) & 0xF
        disp8 = op & 0xFF
        mnemonic = ["bra", "bsr", "bhi", "bls", "bcc", "bcs", "bne", "beq", "bvc", "bvs", "bpl", "bmi", "bge", "blt", "bgt", "ble"][cond]

        if disp8 == 0 and _in_rom(addr, 4, len(data)):
            disp = _signed_word(_be16(data, addr + 2))
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


def disasm_stats(visited: dict[int, Instruction]) -> dict[str, int]:
    unknown = sum(1 for ins in visited.values() if ins.text.startswith("dc.w"))
    terminal = sum(1 for ins in visited.values() if ins.terminal)
    known = len(visited) - unknown
    return {
        "decoded_instructions": len(visited),
        "known_instructions": known,
        "unknown_words": unknown,
        "terminal_instructions": terminal,
    }
