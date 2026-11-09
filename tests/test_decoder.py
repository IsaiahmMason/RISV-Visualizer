import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from decoder import decode

class TestDecoder(unittest.TestCase):
    def test_i_type_addi(self):             # addi a5,zero,5
        d = decode(0x00500793)
        self.assertEqual((d["mnemonic"], d["format"]), ("addi", "I"))
        self.assertEqual(d["fields"]["rd"], "01111")
        self.assertEqual(d["fields"]["rs1"], "00000")
        self.assertEqual(d["fields"]["immediate"], "000000000101")
        self.assertEqual(d["immediate_value"], 5)

    def test_i_type_negative_immediate(self):   # addi sp,sp,-32
        d = decode(0xFE010113)
        self.assertEqual(d["mnemonic"], "addi")
        self.assertEqual(d["immediate_value"], -32)

    def test_load(self):                    # lw a5,-20(s0)
        d = decode(0xFEC42783)
        self.assertEqual(d["mnemonic"], "lw")
        self.assertEqual(d["immediate_value"], -20)

    def test_jalr(self):                    # jalr zero,0(ra)
        d = decode(0x00008067)
        self.assertEqual(d["mnemonic"], "jalr")

    def test_s_type(self):                  # sw s0,28(sp)
        d = decode(0x00812E23)
        self.assertEqual((d["mnemonic"], d["format"]), ("sw", "S"))
        self.assertEqual(d["immediate_value"], 28)
        self.assertNotIn("rd", d["fields"])      # S-type has no rd

    def test_r_type(self):                  # add a0,a0,a1
        d = decode(0x00B50533)
        self.assertEqual((d["mnemonic"], d["format"]), ("add", "R"))
        self.assertEqual(d["fields"]["rs2"], "01011")
        self.assertEqual(d["fields"]["funct7"], "0000000")

    def test_b_type(self):                  # beq a0,zero,+8
        d = decode(0x00050463)
        self.assertEqual((d["mnemonic"], d["format"]), ("beq", "B"))
        self.assertEqual(d["immediate_value"], 8)

    def test_u_type(self):                  # lui a5,0x12
        d = decode(0x000127B7)
        self.assertEqual((d["mnemonic"], d["format"]), ("lui", "U"))
        self.assertEqual(d["immediate_value"], 0x12)

    def test_j_type(self):                  # jal zero,+8
        d = decode(0x0080006F)
        self.assertEqual((d["mnemonic"], d["format"]), ("jal", "J"))
        self.assertEqual(d["immediate_value"], 8)

    def test_unsupported(self):             # ecall
        d = decode(0x00000073)
        self.assertEqual(d["decode_status"], "unsupported")
        self.assertIsNone(d["mnemonic"])

    def test_invalid_combination(self):     # slli with illegal funct7
        d = decode(0x40101013)
        self.assertEqual(d["decode_status"], "invalid")

if __name__ == "__main__":
    unittest.main()