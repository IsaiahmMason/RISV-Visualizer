import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from compiler import compile_source, RequestError

PROGRAMS = {
    "arithmetic": "int main(void) { int x = 2 + 3; return x - 1; }\n",
    "conditional": (
        "int main(void) {\n"
        "    volatile int a = 7;\n"
        "    if (a > 3) { return 1; } else { return 2; }\n"
        "}\n"
    ),
    "loop": (
        "int main(void) {\n"
        "    int sum = 0;\n"
        "    for (int i = 0; i < 10; i++) { sum += i; }\n"
        "    return sum;\n"
        "}\n"
    ),
    "function_call": (
        "static int add(int a, int b) { return a + b; }\n"
        "int main(void) { return add(2, 3); }\n"
    ),
    "array": (
        "int main(void) {\n"
        "    int a[4] = {1, 2, 3, 4};\n"
        "    volatile int i = 2;\n"
        "    return a[i];\n"
        "}\n"
    ),
}

class TestPipeline(unittest.TestCase):
    def test_decoder_matches_objdump(self):
        for name, src in PROGRAMS.items():
            for opt in ("O0", "O2"):
                with self.subTest(program=name, opt=opt):
                    r = compile_source(src, opt)
                    self.assertTrue(r["success"], r.get("diagnostics"))
                    self.assertEqual(len(r["assembly"]), len(r["instructions"]))
                    for asm, ins in zip(r["assembly"], r["instructions"]):
                        self.assertEqual(asm["address"], ins["address"])
                        self.assertEqual(asm["source_line"], ins["source_line"])
                        self.assertNotEqual(ins["decode_status"], "invalid")
                        if ins["decode_status"] == "supported":
                            self.assertEqual(ins["mnemonic"],
                                             asm["text"].split()[0], asm["text"])

    def test_every_instruction_decodes_as_supported(self):
        # Under -march=rv32i, gcc should only emit RV32I instructions.
        for name, src in PROGRAMS.items():
            for opt in ("O0", "O2"):
                with self.subTest(program=name, opt=opt):
                    r = compile_source(src, opt)
                    for ins in r["instructions"]:
                        self.assertEqual(ins["decode_status"], "supported", ins)

    def test_o2_is_smaller_than_o0(self):
        src = PROGRAMS["arithmetic"]
        o0 = compile_source(src, "O0")["instructions"]
        o2 = compile_source(src, "O2")["instructions"]
        self.assertLess(len(o2), len(o0))

    def test_compile_error(self):
        r = compile_source("int main(void) { return 1 }\n", "O0")
        self.assertFalse(r["success"])
        self.assertNotIn("assembly", r)
        text = "\n".join(r["diagnostics"])
        self.assertIn("source.c:1", text)
        self.assertNotIn("/tmp", text)
        self.assertNotIn("/home", text)

    def test_bad_optimization_rejected(self):
        with self.assertRaises(RequestError):
            compile_source("int main(void){return 0;}", "O3")

    def test_empty_source_rejected(self):
        with self.assertRaises(RequestError):
            compile_source("   ", "O0")

    def test_oversized_source_rejected(self):
        with self.assertRaises(RequestError):
            compile_source("a" * (16 * 1024 + 1), "O0")

if __name__ == "__main__":
    unittest.main()