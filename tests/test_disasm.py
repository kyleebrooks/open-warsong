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

    def test_decode_move_indexed_and_pc_relative_to_dn(self) -> None:
        move_w_idx = decode_instruction(bytes.fromhex("343010F8"), 0)
        move_l_pc = decode_instruction(bytes.fromhex("263A0012"), 0)
        move_w_pc_idx = decode_instruction(bytes.fromhex("343BA801"), 0)
        self.assertEqual(move_w_idx.text, "move.w (-8,a0,d1.w),d2")
        self.assertEqual(move_l_pc.text, "move.l (18,pc),d3")
        self.assertEqual(move_w_pc_idx.text, "move.w (1,pc,a2.l),d2")

    def test_decode_move_dn_to_memory_destination(self) -> None:
        move_w_ind = decode_instruction(bytes.fromhex("3490"), 0)
        move_l_post = decode_instruction(bytes.fromhex("2699"), 0)
        move_w_pre = decode_instruction(bytes.fromhex("36A4"), 0)
        move_w_disp = decode_instruction(bytes.fromhex("32A8000C"), 0)
        move_l_abs_w = decode_instruction(bytes.fromhex("22B81234"), 0)
        move_w_abs_l = decode_instruction(bytes.fromhex("32B912345678"), 0)
        self.assertEqual(move_w_ind.text, "move.w d2,(a0)")
        self.assertEqual(move_l_post.text, "move.l d3,(a1)+")
        self.assertEqual(move_w_pre.text, "move.w d3,-(a4)")
        self.assertEqual(move_w_disp.text, "move.w d1,(12,a0)")
        self.assertEqual(move_l_abs_w.text, "move.l d1,($1234).w")
        self.assertEqual(move_w_abs_l.text, "move.w d1,($12345678).l")

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
        cmp_w_pre = decode_instruction(bytes.fromhex("B461"), 0)
        cmp_l_abs_w = decode_instruction(bytes.fromhex("B6B81234"), 0)
        cmp_w_abs_l = decode_instruction(bytes.fromhex("B47912345678"), 0)
        self.assertEqual(cmp_w_pos.text, "cmp.w (18,a0),d2")
        self.assertEqual(cmp_l_neg.text, "cmp.l (-16,a1),d3")
        self.assertEqual(cmp_w_pre.text, "cmp.w -(a1),d2")
        self.assertEqual(cmp_l_abs_w.text, "cmp.l ($1234).w,d3")
        self.assertEqual(cmp_w_abs_l.text, "cmp.w ($12345678).l,d2")

    def test_decode_cmp_indexed_and_pc_relative_to_dn(self) -> None:
        cmp_w_idx = decode_instruction(bytes.fromhex("B47010FC"), 0)
        cmp_l_pc = decode_instruction(bytes.fromhex("B6BA000A"), 0)
        cmp_w_pc_idx = decode_instruction(bytes.fromhex("B47B0802"), 0)
        self.assertEqual(cmp_w_idx.text, "cmp.w (-4,a0,d1.w),d2")
        self.assertEqual(cmp_l_pc.text, "cmp.l (10,pc),d3")
        self.assertEqual(cmp_w_pc_idx.text, "cmp.w (2,pc,d0.l),d2")

    def test_decode_add_sub_dn_to_memory_destination(self) -> None:
        add_w_ind = decode_instruction(bytes.fromhex("D350"), 0)
        sub_l_post = decode_instruction(bytes.fromhex("9799"), 0)
        sub_w_pre = decode_instruction(bytes.fromhex("9764"), 0)
        add_b_disp = decode_instruction(bytes.fromhex("D728FFF8"), 0)
        add_l_abs_w = decode_instruction(bytes.fromhex("D7B81234"), 0)
        sub_b_abs_l = decode_instruction(bytes.fromhex("973912345678"), 0)
        self.assertEqual(add_w_ind.text, "add.w d1,(a0)")
        self.assertEqual(sub_l_post.text, "sub.l d3,(a1)+")
        self.assertEqual(sub_w_pre.text, "sub.w d3,-(a4)")
        self.assertEqual(add_b_disp.text, "add.b d3,(-8,a0)")
        self.assertEqual(add_l_abs_w.text, "add.l d3,($1234).w")
        self.assertEqual(sub_b_abs_l.text, "sub.b d3,($12345678).l")


    def test_decode_add_sub_ea_to_dn(self) -> None:
        add_w_ind = decode_instruction(bytes.fromhex("D450"), 0)
        sub_l_disp = decode_instruction(bytes.fromhex("98A8FFF8"), 0)
        add_w_pc = decode_instruction(bytes.fromhex("D87A0010"), 0)
        sub_b_idx = decode_instruction(bytes.fromhex("98301004"), 0)
        self.assertEqual(add_w_ind.text, "add.w (a0),d2")
        self.assertEqual(sub_l_disp.text, "sub.l (-8,a0),d4")
        self.assertEqual(add_w_pc.text, "add.w (16,pc),d4")
        self.assertEqual(sub_b_idx.text, "sub.b (4,a0,d1.w),d4")



    def test_decode_addi_subi_cmpi_data_alterable_forms(self) -> None:
        subi_b_dn = decode_instruction(bytes.fromhex("0402007F"), 0)
        addi_w_disp = decode_instruction(bytes.fromhex("066800101234"), 0)
        cmpi_l_abs = decode_instruction(bytes.fromhex("0CB90000112212345678"), 0)
        self.assertEqual(subi_b_dn.text, "subi.b #$7F,d2")
        self.assertEqual(subi_b_dn.size, 4)
        self.assertEqual(addi_w_disp.text, "addi.w #$0010,(4660,a0)")
        self.assertEqual(addi_w_disp.size, 6)
        self.assertEqual(cmpi_l_abs.text, "cmpi.l #$00001122,($12345678).l")
        self.assertEqual(cmpi_l_abs.size, 10)

    def test_decode_immediate_logic_forms(self) -> None:
        ori_b_dn = decode_instruction(bytes.fromhex("0002007F"), 0)
        andi_w_mem = decode_instruction(bytes.fromhex("026800101234"), 0)
        eori_l_abs = decode_instruction(bytes.fromhex("0AB90000112212345678"), 0)
        self.assertEqual(ori_b_dn.text, "ori.b #$7F,d2")
        self.assertEqual(ori_b_dn.size, 4)
        self.assertEqual(andi_w_mem.text, "andi.w #$0010,(4660,a0)")
        self.assertEqual(andi_w_mem.size, 6)
        self.assertEqual(eori_l_abs.text, "eori.l #$00001122,($12345678).l")
        self.assertEqual(eori_l_abs.size, 10)



    def test_decode_immediate_logic_control_register_forms(self) -> None:
        ori_ccr = decode_instruction(bytes.fromhex("003C00F0"), 0)
        ori_sr = decode_instruction(bytes.fromhex("007C2700"), 0)
        andi_ccr = decode_instruction(bytes.fromhex("023C0007"), 0)
        andi_sr = decode_instruction(bytes.fromhex("027CFF00"), 0)
        eori_ccr = decode_instruction(bytes.fromhex("0A3C001F"), 0)
        eori_sr = decode_instruction(bytes.fromhex("0A7C2000"), 0)
        self.assertEqual(ori_ccr.text, "ori.w #$F0,ccr")
        self.assertEqual(ori_sr.text, "ori.w #$2700,sr")
        self.assertEqual(andi_ccr.text, "andi.w #$07,ccr")
        self.assertEqual(andi_sr.text, "andi.w #$FF00,sr")
        self.assertEqual(eori_ccr.text, "eori.w #$1F,ccr")
        self.assertEqual(eori_sr.text, "eori.w #$2000,sr")

    def test_decode_bit_manipulation_register_forms(self) -> None:
        btst_dn = decode_instruction(bytes.fromhex("0102"), 0)
        bchg_mem = decode_instruction(bytes.fromhex("0750"), 0)
        bclr_abs = decode_instruction(bytes.fromhex("09B81234"), 0)
        bset_pre = decode_instruction(bytes.fromhex("0BE4"), 0)
        self.assertEqual(btst_dn.text, "btst d0,d2")
        self.assertEqual(bchg_mem.text, "bchg d3,(a0)")
        self.assertEqual(bclr_abs.text, "bclr d4,($1234).w")
        self.assertEqual(bset_pre.text, "bset d5,-(a4)")

    def test_decode_bit_manipulation_immediate_forms(self) -> None:
        btst_imm_dn = decode_instruction(bytes.fromhex("08020007"), 0)
        bchg_imm_mem = decode_instruction(bytes.fromhex("08500003"), 0)
        bclr_imm_disp = decode_instruction(bytes.fromhex("08A8001FFFF8"), 0)
        bset_imm_abs = decode_instruction(bytes.fromhex("08F9000500123456"), 0)
        self.assertEqual(btst_imm_dn.text, "btst #$07,d2")
        self.assertEqual(btst_imm_dn.size, 4)
        self.assertEqual(bchg_imm_mem.text, "bchg #$03,(a0)")
        self.assertEqual(bchg_imm_mem.size, 4)
        self.assertEqual(bclr_imm_disp.text, "bclr #$1F,(-8,a0)")
        self.assertEqual(bclr_imm_disp.size, 6)
        self.assertEqual(bset_imm_abs.text, "bset #$05,($00123456).l")
        self.assertEqual(bset_imm_abs.size, 8)
    def test_decode_dbcc(self) -> None:
        dbne = decode_instruction(bytes.fromhex("56CBFFFC"), 0)
        dbra = decode_instruction(bytes.fromhex("51C80006"), 0)
        self.assertEqual(dbne.text, "dbne d3,loc_000000")
        self.assertEqual(dbne.flow_targets, [0])
        self.assertEqual(dbra.text, "dbra d0,loc_00000A")





    def test_decode_cmpa_forms(self) -> None:
        cmpa_w = decode_instruction(bytes.fromhex("B4E8FFF0"), 0)
        cmpa_l = decode_instruction(bytes.fromhex("B7FB2802"), 0)
        cmpa_imm = decode_instruction(bytes.fromhex("B6FC12345678"), 0)
        self.assertEqual(cmpa_w.text, "cmpa.w (-16,a0),a2")
        self.assertEqual(cmpa_l.text, "cmpa.l (2,pc,d2.l),a3")
        self.assertEqual(cmpa_imm.text, "cmpa.w #$1234,a3")

    def test_decode_cmpm_postincrement_forms(self) -> None:
        cmpm_b = decode_instruction(bytes.fromhex("B70D"), 0)
        cmpm_w = decode_instruction(bytes.fromhex("B54C"), 0)
        cmpm_l = decode_instruction(bytes.fromhex("B98E"), 0)
        self.assertEqual(cmpm_b.text, "cmpm.b (a5)+,(a3)+")
        self.assertEqual(cmpm_w.text, "cmpm.w (a4)+,(a2)+")
        self.assertEqual(cmpm_l.text, "cmpm.l (a6)+,(a4)+")

    def test_decode_or_and_ea_and_memory_destination_forms(self) -> None:
        or_w_from_ea = decode_instruction(bytes.fromhex("8650"), 0)
        and_l_from_ea = decode_instruction(bytes.fromhex("CAAAFFF8"), 0)
        or_b_to_ea = decode_instruction(bytes.fromhex("8710"), 0)
        and_w_to_abs = decode_instruction(bytes.fromhex("C7781234"), 0)
        self.assertEqual(or_w_from_ea.text, "or.w (a0),d3")
        self.assertEqual(and_l_from_ea.text, "and.l (-8,a2),d5")
        self.assertEqual(or_b_to_ea.text, "or.b d3,(a0)")
        self.assertEqual(and_w_to_abs.text, "and.w d3,($1234).w")






    def test_decode_exg_register_forms(self) -> None:
        exg_dd = decode_instruction(bytes.fromhex("C745"), 0)
        exg_aa = decode_instruction(bytes.fromhex("C94E"), 0)
        exg_da = decode_instruction(bytes.fromhex("CB8D"), 0)
        self.assertEqual(exg_dd.text, "exg d3,d5")
        self.assertEqual(exg_aa.text, "exg a4,a6")
        self.assertEqual(exg_da.text, "exg d5,a5")

    def test_decode_eor_dn_to_memory_destination_forms(self) -> None:
        eor_b_ind = decode_instruction(bytes.fromhex("B710"), 0)
        eor_w_disp = decode_instruction(bytes.fromhex("B768FFF8"), 0)
        eor_l_abs_l = decode_instruction(bytes.fromhex("B7B912345678"), 0)
        self.assertEqual(eor_b_ind.text, "eor.b d3,(a0)")
        self.assertEqual(eor_w_disp.text, "eor.w d3,(-8,a0)")
        self.assertEqual(eor_l_abs_l.text, "eor.l d3,($12345678).l")

    def test_decode_jsr_jmp_control_forms(self) -> None:
        jsr_pc = decode_instruction(bytes.fromhex("4EBA0010"), 0)
        jmp_pc = decode_instruction(bytes.fromhex("4EFAFFFE"), 0)
        jmp_idx = decode_instruction(bytes.fromhex("4EF02804"), 0)
        self.assertEqual(jsr_pc.text, "jsr loc_000012")
        self.assertEqual(jsr_pc.flow_targets, [0x12])
        self.assertEqual(jmp_pc.text, "jmp loc_000000")
        self.assertEqual(jmp_pc.flow_targets, [0])
        self.assertEqual(jmp_idx.text, "jmp (4,a0,d2.l)")
        self.assertTrue(jmp_idx.terminal)

    def test_decode_jsr_jmp_abs_word(self) -> None:
        jsr = decode_instruction(bytes.fromhex("4EB81234"), 0)
        jmp = decode_instruction(bytes.fromhex("4EF80040"), 0)
        self.assertEqual(jsr.text, "jsr loc_001234")
        self.assertEqual(jsr.flow_targets, [0x1234])
        self.assertEqual(jmp.text, "jmp loc_000040")
        self.assertTrue(jmp.terminal)


    def test_decode_lea_control_forms(self) -> None:
        lea_disp = decode_instruction(bytes.fromhex("43E8FFF0"), 0)
        lea_idx = decode_instruction(bytes.fromhex("45F01008"), 0)
        lea_pc = decode_instruction(bytes.fromhex("47FA0012"), 0)
        lea_pc_idx = decode_instruction(bytes.fromhex("49FB2801"), 0)
        self.assertEqual(lea_disp.text, "lea (-16,a0),a1")
        self.assertEqual(lea_idx.text, "lea (8,a0,d1.w),a2")
        self.assertEqual(lea_pc.text, "lea (18,pc),a3")
        self.assertEqual(lea_pc_idx.text, "lea (1,pc,d2.l),a4")

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
