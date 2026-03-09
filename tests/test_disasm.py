from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "open-warsong"))

from disasm import decode_instruction, walk_code


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


if __name__ == "__main__":
    unittest.main()
