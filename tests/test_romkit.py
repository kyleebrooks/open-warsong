from pathlib import Path
import sys
import unittest
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "open-warsong"))

from romkit import (
    apply_byte_patches,
    apply_ips,
    compute_genesis_checksum,
    with_updated_header_checksum,
    write_ips,
)


class RomkitTests(unittest.TestCase):
    def test_checksum_roundtrip(self) -> None:
        data = bytes([0] * 0x400)
        patched = bytearray(data)
        patched[0x220] = 0x12
        patched[0x221] = 0x34

        updated = with_updated_header_checksum(bytes(patched))
        expected = compute_genesis_checksum(bytes(patched))
        self.assertEqual(updated[0x18E], (expected >> 8) & 0xFF)
        self.assertEqual(updated[0x18F], expected & 0xFF)

    def test_apply_byte_patches_expect_success(self) -> None:
        data = bytes([0x11, 0x22, 0x33, 0x44])
        out = apply_byte_patches(data, [{"offset": "0x1", "expect": "22", "bytes": "AA BB"}])
        self.assertEqual(out, bytes([0x11, 0xAA, 0xBB, 0x44]))

    def test_apply_byte_patches_expect_mismatch(self) -> None:
        data = bytes([0x11, 0x22, 0x33, 0x44])
        with self.assertRaises(ValueError):
            apply_byte_patches(data, [{"offset": "0x1", "expect": "99", "bytes": "AA"}])


    def test_apply_ips_rle_record(self) -> None:
        base = bytes([0] * 32)
        # PATCH + offset(3) + size(2=0 for RLE) + rle_size(2) + value(1) + EOF
        ips = b"PATCH" + bytes([0x00,0x00,0x08]) + bytes([0x00,0x00]) + bytes([0x00,0x04]) + bytes([0x7F]) + b"EOF"
        out = apply_ips(base, ips)
        self.assertEqual(out[8:12], bytes([0x7F,0x7F,0x7F,0x7F]))

    def test_ips_roundtrip(self) -> None:
        base = bytes([0] * 256)
        modified = bytearray(base)
        modified[10:14] = b"ABCD"
        modified[200:203] = b"XYZ"

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "patch.ips"
            write_ips(base, bytes(modified), p)
            applied = apply_ips(base, p.read_bytes())
            self.assertEqual(applied, bytes(modified))


if __name__ == "__main__":
    unittest.main()
