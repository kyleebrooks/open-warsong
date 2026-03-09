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


def _decode_indexed_brief(ext: int, base: str) -> str:
    idx_is_addr = bool(ext & 0x8000)
    idx_reg = (ext >> 12) & 0x7
    idx_size = "l" if (ext & 0x0800) else "w"
    disp = (ext & 0xFF) - 0x100 if ext & 0x80 else (ext & 0xFF)
    idx_prefix = "a" if idx_is_addr else "d"
    return f"({disp},{base},{idx_prefix}{idx_reg}.{idx_size})"


def _decode_memory_ea(op: int, data: bytes, addr: int, ext_offset: int = 2) -> tuple[str, int] | None:
    mode = (op >> 3) & 0x7
    reg = op & 0x7
    if mode == 2:
        return f"(a{reg})", 2
    if mode == 3:
        return f"(a{reg})+", 2
    if mode == 4:
        return f"-(a{reg})", 2
    if mode == 5 and _in_rom(addr, ext_offset + 2, len(data)):
        disp = _signed_word(_be16(data, addr + ext_offset))
        return f"({disp},a{reg})", ext_offset + 2
    if mode == 6 and _in_rom(addr, ext_offset + 2, len(data)):
        ext = _be16(data, addr + ext_offset)
        return _decode_indexed_brief(ext, f"a{reg}"), ext_offset + 2
    if mode == 7 and reg == 0 and _in_rom(addr, ext_offset + 2, len(data)):
        abs_word = _be16(data, addr + ext_offset)
        return f"(${abs_word:04X}).w", ext_offset + 2
    if mode == 7 and reg == 1 and _in_rom(addr, ext_offset + 4, len(data)):
        abs_long = _be32(data, addr + ext_offset)
        return f"(${abs_long:08X}).l", ext_offset + 4
    if mode == 7 and reg == 2 and _in_rom(addr, ext_offset + 2, len(data)):
        disp = _signed_word(_be16(data, addr + ext_offset))
        return f"({disp},pc)", ext_offset + 2
    if mode == 7 and reg == 3 and _in_rom(addr, ext_offset + 2, len(data)):
        ext = _be16(data, addr + ext_offset)
        return _decode_indexed_brief(ext, "pc"), ext_offset + 2
    return None


def _decode_data_ea(op: int, data: bytes, addr: int) -> tuple[str, int] | None:
    decoded = _decode_memory_ea(op, data, addr)
    if decoded is not None:
        return decoded
    mode = (op >> 3) & 0x7
    reg = op & 0x7
    if mode == 0:
        return f"d{reg}", 2
    if mode == 1:
        return f"a{reg}", 2
    if mode == 7 and reg == 4 and _in_rom(addr, 4, len(data)):
        imm = _be16(data, addr + 2)
        return f"#${imm:04X}", 4
    return None


def _decode_control_ea(op: int, data: bytes, addr: int) -> tuple[str, int] | None:
    mode = (op >> 3) & 0x7
    reg = op & 0x7
    if mode == 2:
        return f"(a{reg})", 2
    if mode == 5 and _in_rom(addr, 4, len(data)):
        disp = _signed_word(_be16(data, addr + 2))
        return f"({disp},a{reg})", 4
    if mode == 6 and _in_rom(addr, 4, len(data)):
        ext = _be16(data, addr + 2)
        return _decode_indexed_brief(ext, f"a{reg}"), 4
    if mode == 7 and reg == 0 and _in_rom(addr, 4, len(data)):
        abs_word = _be16(data, addr + 2)
        return f"loc_{abs_word:06X}", 4
    if mode == 7 and reg == 1 and _in_rom(addr, 6, len(data)):
        abs_long = _be32(data, addr + 2)
        return f"loc_{abs_long:06X}", 6
    if mode == 7 and reg == 2 and _in_rom(addr, 4, len(data)):
        disp = _signed_word(_be16(data, addr + 2))
        return f"({disp},pc)", 4
    if mode == 7 and reg == 3 and _in_rom(addr, 4, len(data)):
        ext = _be16(data, addr + 2)
        return _decode_indexed_brief(ext, "pc"), 4
    return None


def _decode_data_alterable_ea(op: int, data: bytes, addr: int, ext_offset: int = 2) -> tuple[str, int] | None:
    mode = (op >> 3) & 0x7
    reg = op & 0x7
    if mode == 0:
        return f"d{reg}", 2
    return _decode_memory_ea(op, data, addr, ext_offset)


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

    # MOVE indexed and PC-relative forms to data register.
    if (op & 0xF1F8) == 0x3030 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        ext = _be16(data, addr + 2)
        return Instruction(addr, 4, f"move.w {_decode_indexed_brief(ext, f'a{src}')},d{dst}", [])
    if (op & 0xF1F8) == 0x2030 and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        src = op & 0x7
        ext = _be16(data, addr + 2)
        return Instruction(addr, 4, f"move.l {_decode_indexed_brief(ext, f'a{src}')},d{dst}", [])
    if (op & 0xF1FF) == 0x303A and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"move.w ({disp},pc),d{dst}", [])
    if (op & 0xF1FF) == 0x203A and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        return Instruction(addr, 4, f"move.l ({disp},pc),d{dst}", [])
    if (op & 0xF1FF) == 0x303B and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        ext = _be16(data, addr + 2)
        return Instruction(addr, 4, f"move.w {_decode_indexed_brief(ext, 'pc')},d{dst}", [])
    if (op & 0xF1FF) == 0x203B and _in_rom(addr, 4, len(data)):
        dst = (op >> 9) & 0x7
        ext = _be16(data, addr + 2)
        return Instruction(addr, 4, f"move.l {_decode_indexed_brief(ext, 'pc')},d{dst}", [])

    # MOVE data register to memory destination.
    if (op & 0xF1C0) in (0x3080, 0x2080):
        src = (op >> 9) & 0x7
        size = "w" if (op & 0xF1C0) == 0x3080 else "l"
        decoded = _decode_memory_ea(op, data, addr)
        if decoded is not None:
            ea_text, ins_size = decoded
            return Instruction(addr, ins_size, f"move.{size} d{src},{ea_text}", [])

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

    # ADDI/SUBI/CMPI #imm,<ea> subset across data-alterable EA families.
    imm_arith_family = {
        0x0400: "subi",
        0x0600: "addi",
        0x0C00: "cmpi",
    }.get(op & 0xFF00)
    if imm_arith_family is not None:
        size_bits = (op >> 6) & 0x3
        if size_bits == 0 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2) & 0x00FF
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=4)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 4), f"{imm_arith_family}.b #${imm:02X},{ea_text}", [])
        if size_bits == 1 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2)
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=4)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 4), f"{imm_arith_family}.w #${imm:04X},{ea_text}", [])
        if size_bits == 2 and _in_rom(addr, 6, len(data)):
            imm = _be32(data, addr + 2)
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=6)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 6), f"{imm_arith_family}.l #${imm:08X},{ea_text}", [])

    # ORI/ANDI/EORI to CCR/SR control variants.
    imm_control_family = {
        0x003C: ("ori", "ccr"),
        0x007C: ("ori", "sr"),
        0x023C: ("andi", "ccr"),
        0x027C: ("andi", "sr"),
        0x0A3C: ("eori", "ccr"),
        0x0A7C: ("eori", "sr"),
    }.get(op)
    if imm_control_family is not None and _in_rom(addr, 4, len(data)):
        mnemonic, dst = imm_control_family
        imm = _be16(data, addr + 2)
        imm_text = f"#${imm & 0x00FF:02X}" if dst == "ccr" else f"#${imm:04X}"
        return Instruction(addr, 4, f"{mnemonic}.w {imm_text},{dst}", [])

    # ORI/ANDI/EORI #imm,<ea> subset across data-alterable EA families.
    imm_family = {
        0x0000: "ori",
        0x0200: "andi",
        0x0A00: "eori",
    }.get(op & 0xFF00)
    if imm_family is not None:
        size_bits = (op >> 6) & 0x3
        if size_bits == 0 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2) & 0x00FF
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=4)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 4), f"{imm_family}.b #${imm:02X},{ea_text}", [])
        if size_bits == 1 and _in_rom(addr, 4, len(data)):
            imm = _be16(data, addr + 2)
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=4)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 4), f"{imm_family}.w #${imm:04X},{ea_text}", [])
        if size_bits == 2 and _in_rom(addr, 6, len(data)):
            imm = _be32(data, addr + 2)
            decoded = _decode_data_alterable_ea(op, data, addr, ext_offset=6)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, max(ins_size, 6), f"{imm_family}.l #${imm:08X},{ea_text}", [])

    # BTST/BCHG/BCLR/BSET bit-manipulation families.
    bitop_reg_family = {
        0x0100: ("btst", _decode_data_ea),
        0x0140: ("bchg", _decode_data_alterable_ea),
        0x0180: ("bclr", _decode_data_alterable_ea),
        0x01C0: ("bset", _decode_data_alterable_ea),
    }.get(op & 0xF1C0)
    if bitop_reg_family is not None:
        mnemonic, ea_decoder = bitop_reg_family
        bit_reg = (op >> 9) & 0x7
        decoded = ea_decoder(op, data, addr)
        if decoded is not None:
            ea_text, ins_size = decoded
            return Instruction(addr, ins_size, f"{mnemonic} d{bit_reg},{ea_text}", [])

    bitop_imm_family = {
        0x0800: ("btst", _decode_data_ea),
        0x0840: ("bchg", _decode_data_alterable_ea),
        0x0880: ("bclr", _decode_data_alterable_ea),
        0x08C0: ("bset", _decode_data_alterable_ea),
    }.get(op & 0xFFC0)
    if bitop_imm_family is not None and _in_rom(addr, 4, len(data)):
        mnemonic, ea_decoder = bitop_imm_family
        bit_imm = _be16(data, addr + 2) & 0x00FF
        if ea_decoder is _decode_data_ea:
            decoded = ea_decoder(op, data, addr)
        else:
            decoded = ea_decoder(op, data, addr, ext_offset=4)
        if decoded is not None:
            ea_text, ins_size = decoded
            return Instruction(addr, max(ins_size, 4), f"{mnemonic} #${bit_imm:02X},{ea_text}", [])

    # DBcc Dn,<disp16>
    if (op & 0xF0F8) == 0x50C8 and _in_rom(addr, 4, len(data)):
        cond = (op >> 8) & 0xF
        reg = op & 0x7
        disp = _signed_word(_be16(data, addr + 2))
        target = (addr + 4 + disp) & 0xFFFFFFFF
        mnemonic = DBCC_MNEMONICS[cond]
        return Instruction(addr, 4, f"{mnemonic} d{reg},loc_{target:06X}", [target])

    # CMPA <ea>,An forms.
    if (op & 0xF000) == 0xB000:
        opmode = (op >> 6) & 0x7
        size = {3: "w", 7: "l"}.get(opmode)
        if size is not None:
            dst = (op >> 9) & 0x7
            decoded = _decode_data_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, ins_size, f"cmpa.{size} {ea_text},a{dst}", [])

    # CMP (An)/(An)+,Dn subset.
    if (op & 0xF000) == 0xB000:
        opmode = (op >> 6) & 0x7
        size = {0: "b", 1: "w", 2: "l"}.get(opmode)
        if size is not None:
            dst = (op >> 9) & 0x7
            decoded = _decode_memory_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, ins_size, f"cmp.{size} {ea_text},d{dst}", [])

    # CMPM (Ay)+,(Ax)+ forms.
    if (op & 0xF138) == 0xB108:
        size = {4: "b", 5: "w", 6: "l"}.get((op >> 6) & 0x7)
        if size is not None:
            dst = (op >> 9) & 0x7
            src = op & 0x7
            return Instruction(addr, 2, f"cmpm.{size} (a{src})+,(a{dst})+", [])

    # ADD/SUB Dn,<ea> subset for common memory destinations.
    op_class = op & 0xF000
    if op_class in (0x9000, 0xD000):
        opmode = (op >> 6) & 0x7
        size = {4: "b", 5: "w", 6: "l"}.get(opmode)
        if size is not None:
            src = (op >> 9) & 0x7
            decoded = _decode_memory_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                mnemonic = "sub" if op_class == 0x9000 else "add"
                return Instruction(addr, ins_size, f"{mnemonic}.{size} d{src},{ea_text}", [])

    # ADD/SUB <ea>,Dn subset (supports indexed and PC-relative forms).
    if op_class in (0x9000, 0xD000):
        opmode = (op >> 6) & 0x7
        size = {0: "b", 1: "w", 2: "l"}.get(opmode)
        if size is not None:
            dst = (op >> 9) & 0x7
            decoded = _decode_data_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                mnemonic = "sub" if op_class == 0x9000 else "add"
                return Instruction(addr, ins_size, f"{mnemonic}.{size} {ea_text},d{dst}", [])

    if op == 0x4E56 and _in_rom(addr, 4, len(data)):
        imm = _be16(data, addr + 2)
        return Instruction(addr, 4, f"link a6,#${imm:04X}", [])
    if op == 0x4E5E:
        return Instruction(addr, 2, "unlk a6", [])

    # OR/AND Dn,<ea> and <ea>,Dn subsets over decoded EA families.
    if op_class in (0x8000, 0xC000):
        mnemonic = "or" if op_class == 0x8000 else "and"
        opmode = (op >> 6) & 0x7
        src_or_dst = (op >> 9) & 0x7

        size_from_ea = {0: "b", 1: "w", 2: "l"}.get(opmode)
        if size_from_ea is not None:
            decoded = _decode_data_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, ins_size, f"{mnemonic}.{size_from_ea} {ea_text},d{src_or_dst}", [])

        size_to_ea = {4: "b", 5: "w", 6: "l"}.get(opmode)
        if size_to_ea is not None:
            decoded = _decode_memory_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, ins_size, f"{mnemonic}.{size_to_ea} d{src_or_dst},{ea_text}", [])

    # EXG register exchange forms.
    if (op & 0xF1F8) == 0xC140:
        rx = (op >> 9) & 0x7
        ry = op & 0x7
        return Instruction(addr, 2, f"exg d{rx},d{ry}", [])
    if (op & 0xF1F8) == 0xC148:
        rx = (op >> 9) & 0x7
        ry = op & 0x7
        return Instruction(addr, 2, f"exg a{rx},a{ry}", [])
    if (op & 0xF1F8) == 0xC188:
        rx = (op >> 9) & 0x7
        ry = op & 0x7
        return Instruction(addr, 2, f"exg d{rx},a{ry}", [])

    # EOR Dn,<ea> subset over decoded memory EA families.
    if (op & 0xF100) == 0xB100:
        reg = (op >> 9) & 0x7
        size = {0: "b", 1: "w", 2: "l"}.get((op >> 6) & 0x3)
        if size is not None:
            decoded = _decode_memory_ea(op, data, addr)
            if decoded is not None:
                ea_text, ins_size = decoded
                return Instruction(addr, ins_size, f"eor.{size} d{reg},{ea_text}", [])

    # JSR/JMP control-addressing forms.
    if (op & 0xFFC0) == 0x4E80:
        decoded = _decode_control_ea(op, data, addr)
        if decoded is not None:
            ea_text, ins_size = decoded
            mode = (op >> 3) & 0x7
            reg = op & 0x7
            targets: list[int] = []
            if mode == 7 and reg == 0 and _in_rom(addr, 4, len(data)):
                target = _be16(data, addr + 2)
                targets = [target]
                ea_text = f"loc_{target:06X}"
            if mode == 7 and reg == 1 and _in_rom(addr, 6, len(data)):
                target = _be32(data, addr + 2)
                targets = [target]
                ea_text = f"loc_{target:06X}"
            if mode == 7 and reg == 2 and _in_rom(addr, 4, len(data)):
                disp = _signed_word(_be16(data, addr + 2))
                target = (addr + 2 + disp) & 0xFFFFFFFF
                targets = [target]
                ea_text = f"loc_{target:06X}"
            return Instruction(addr, ins_size, f"jsr {ea_text}", targets)

    if (op & 0xFFC0) == 0x4EC0:
        decoded = _decode_control_ea(op, data, addr)
        if decoded is not None:
            ea_text, ins_size = decoded
            mode = (op >> 3) & 0x7
            reg = op & 0x7
            targets: list[int] = []
            if mode == 7 and reg == 0 and _in_rom(addr, 4, len(data)):
                target = _be16(data, addr + 2)
                targets = [target]
                ea_text = f"loc_{target:06X}"
            if mode == 7 and reg == 1 and _in_rom(addr, 6, len(data)):
                target = _be32(data, addr + 2)
                targets = [target]
                ea_text = f"loc_{target:06X}"
            if mode == 7 and reg == 2 and _in_rom(addr, 4, len(data)):
                disp = _signed_word(_be16(data, addr + 2))
                target = (addr + 2 + disp) & 0xFFFFFFFF
                targets = [target]
                ea_text = f"loc_{target:06X}"
            return Instruction(addr, ins_size, f"jmp {ea_text}", targets, True)

    # LEA control-addressing forms.
    if (op & 0xF1C0) == 0x41C0:
        reg = (op >> 9) & 0x7
        decoded = _decode_control_ea(op, data, addr)
        if decoded is not None:
            ea_text, ins_size = decoded
            return Instruction(addr, ins_size, f"lea {ea_text},a{reg}", [])

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
