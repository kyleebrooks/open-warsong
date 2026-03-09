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

    def test_disasm_stats_counts_unknown(self) -> None:
        visited, _ = walk_code(bytes.fromhex("4E714E754AFC"), [0, 4])
        stats = disasm_stats(visited)
        self.assertEqual(stats["decoded_instructions"], 3)
        self.assertEqual(stats["unknown_words"], 1)
        self.assertEqual(stats["known_instructions"], 2)

if __name__ == "__main__":
    unittest.main()
