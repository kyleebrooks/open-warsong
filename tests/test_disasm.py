from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "open-warsong"))

from disasm import decode_instruction, walk_code, disasm_stats


class DisasmTests(unittest.TestCase):
    def test_decode_rts(self) -> None:
        data = bytes.fromhex("4E75")
        ins = decode_instruction(data, 0)
        self.assertEqual(ins.text, "rts")
        self.assertTrue(ins.terminal)

    def test_decode_jsr_abs_long(self) -> None:
        data = bytes.fromhex("4EB900001234")
        ins = decode_instruction(data, 0)
        self.assertEqual(ins.size, 6)
        self.assertEqual(ins.flow_targets, [0x1234])

    def test_decode_bra_short(self) -> None:
        data = bytes.fromhex("6002") + bytes.fromhex("4E75")
        ins = decode_instruction(data, 0)
        self.assertIn("bra.s", ins.text)
        self.assertEqual(ins.flow_targets, [4])

    def test_walk_code_follows_branch_targets(self) -> None:
        # 0000: bra.s +2 -> 0004
        # 0002: nop
        # 0004: rts
        data = bytes.fromhex("60024E714E75")
        visited, labels = walk_code(data, [0])
        self.assertIn(0, visited)
        self.assertIn(4, labels)
        self.assertIn(4, visited)

    def test_decode_moveq(self) -> None:
        data = bytes.fromhex("7010")
        ins = decode_instruction(data, 0)
        self.assertEqual(ins.text, "moveq #16,d0")

    def test_decode_addq_subq_dn(self) -> None:
        add = decode_instruction(bytes.fromhex("5281"), 0)
        sub = decode_instruction(bytes.fromhex("5102"), 0)
        self.assertEqual(add.text, "addq.l #1,d1")
        self.assertEqual(sub.text, "subq.b #8,d2")


    def test_decode_move_immediate_dn(self) -> None:
        word = decode_instruction(bytes.fromhex("323C1234"), 0)
        longw = decode_instruction(bytes.fromhex("243C89ABCDEF"), 0)
        self.assertEqual(word.text, "move.w #$1234,d1")
        self.assertEqual(longw.text, "move.l #$89ABCDEF,d2")

    def test_decode_move_address_indirect_to_dn(self) -> None:
        move_w = decode_instruction(bytes.fromhex("3412"), 0)
        move_l = decode_instruction(bytes.fromhex("2616"), 0)
        move_w_post = decode_instruction(bytes.fromhex("3218"), 0)
        move_l_post = decode_instruction(bytes.fromhex("2419"), 0)
        self.assertEqual(move_w.text, "move.w (a2),d2")
        self.assertEqual(move_l.text, "move.l (a6),d3")
        self.assertEqual(move_w_post.text, "move.w (a0)+,d1")
        self.assertEqual(move_l_post.text, "move.l (a1)+,d2")

    def test_decode_move_displacement_address_indirect_to_dn(self) -> None:
        move_w_pos = decode_instruction(bytes.fromhex("322A0010"), 0)
        move_l_neg = decode_instruction(bytes.fromhex("242BFFF8"), 0)
        self.assertEqual(move_w_pos.text, "move.w (16,a2),d1")
        self.assertEqual(move_l_neg.text, "move.l (-8,a3),d2")

    def test_decode_clr_tst_dn(self) -> None:
        clr = decode_instruction(bytes.fromhex("4282"), 0)
        tst = decode_instruction(bytes.fromhex("4A40"), 0)
        self.assertEqual(clr.text, "clr.l d2")
        self.assertEqual(tst.text, "tst.w d0")

    def test_decode_cmpi_dn(self) -> None:
        b = decode_instruction(bytes.fromhex("0C02007F"), 0)
        w = decode_instruction(bytes.fromhex("0C430123"), 0)
        l = decode_instruction(bytes.fromhex("0C84DEADBEEF"), 0)
        self.assertEqual(b.text, "cmpi.b #$7F,d2")
        self.assertEqual(w.text, "cmpi.w #$0123,d3")
        self.assertEqual(l.text, "cmpi.l #$DEADBEEF,d4")


    def test_decode_cmp_address_indirect_to_dn(self) -> None:
        cmp_w = decode_instruction(bytes.fromhex("B452"), 0)
        cmp_l = decode_instruction(bytes.fromhex("B696"), 0)
        cmp_w_post = decode_instruction(bytes.fromhex("B258"), 0)
        cmp_l_post = decode_instruction(bytes.fromhex("B499"), 0)
        self.assertEqual(cmp_w.text, "cmp.w (a2),d2")
        self.assertEqual(cmp_l.text, "cmp.l (a6),d3")
        self.assertEqual(cmp_w_post.text, "cmp.w (a0)+,d1")
        self.assertEqual(cmp_l_post.text, "cmp.l (a1)+,d2")

    def test_decode_cmp_displacement_address_indirect_to_dn(self) -> None:
        cmp_w_pos = decode_instruction(bytes.fromhex("B4680012"), 0)
        cmp_l_neg = decode_instruction(bytes.fromhex("B6A9FFF0"), 0)
        self.assertEqual(cmp_w_pos.text, "cmp.w (18,a0),d2")
        self.assertEqual(cmp_l_neg.text, "cmp.l (-16,a1),d3")

    def test_decode_dbcc(self) -> None:
        dbne = decode_instruction(bytes.fromhex("56CBFFFC"), 0)
        dbra = decode_instruction(bytes.fromhex("51C80006"), 0)
        self.assertEqual(dbne.text, "dbne d3,loc_000000")
        self.assertEqual(dbne.flow_targets, [0])
        self.assertEqual(dbra.text, "dbra d0,loc_00000A")


    def test_decode_jsr_jmp_abs_word(self) -> None:
        jsr = decode_instruction(bytes.fromhex("4EB81234"), 0)
        jmp = decode_instruction(bytes.fromhex("4EF80040"), 0)
        self.assertEqual(jsr.text, "jsr loc_001234")
        self.assertEqual(jsr.flow_targets, [0x1234])
        self.assertEqual(jmp.text, "jmp loc_000040")
        self.assertTrue(jmp.terminal)

    def test_decode_lea_abs_and_movea_immediate(self) -> None:
        lea_w = decode_instruction(bytes.fromhex("45F80080"), 0)
        lea_l = decode_instruction(bytes.fromhex("47F900123456"), 0)
        movea_w = decode_instruction(bytes.fromhex("347C1234"), 0)
        movea_l = decode_instruction(bytes.fromhex("267C89ABCDEF"), 0)
        self.assertEqual(lea_w.text, "lea loc_000080,a2")
        self.assertEqual(lea_l.text, "lea loc_123456,a3")
        self.assertEqual(movea_w.text, "movea.w #$1234,a2")
        self.assertEqual(movea_l.text, "movea.l #$89ABCDEF,a3")

    def test_disasm_stats_counts_unknown(self) -> None:
        visited, _ = walk_code(bytes.fromhex("4E714E754AFC"), [0, 4])
        stats = disasm_stats(visited)
        self.assertEqual(stats["decoded_instructions"], 3)
        self.assertEqual(stats["unknown_words"], 1)
        self.assertEqual(stats["known_instructions"], 2)

if __name__ == "__main__":
    unittest.main()
