"""RV32I instruction decoder (design doc Section 5)."""

def _bits(w, hi, lo):
    """Extract bits hi..lo (inclusive) from w."""
    return (w >> lo) & ((1 << (hi - lo + 1)) - 1)

def _sext(value, width):
    """Sign-extend a width-bit value to a Python int."""
    return value - (1 << width) if value & (1 << (width - 1)) else value

def _b(value, width):
    """Format value as a width-bit binary string."""
    return f"{value:0{width}b}"

R_OPS = {
    (0, 0x00): "add", (0, 0x20): "sub", (1, 0x00): "sll",
    (2, 0x00): "slt", (3, 0x00): "sltu", (4, 0x00): "xor",
    (5, 0x00): "srl", (5, 0x20): "sra", (6, 0x00): "or",
    (7, 0x00): "and",
}
I_ALU = {0: "addi", 2: "slti", 3: "sltiu", 4: "xori", 6: "ori", 7: "andi"}
LOADS = {0: "lb", 1: "lh", 2: "lw", 4: "lbu", 5: "lhu"}
STORES = {0: "sb", 1: "sh", 2: "sw"}
BRANCHES = {0: "beq", 1: "bne", 4: "blt", 5: "bge", 6: "bltu", 7: "bgeu"}

def decode(word):
    """Decode one 32-bit word into a dict. Only meaningful fields appear."""
    word &= 0xFFFFFFFF
    opcode = _bits(word, 6, 0)
    rd, funct3 = _bits(word, 11, 7), _bits(word, 14, 12)
    rs1, rs2, funct7 = _bits(word, 19, 15), _bits(word, 24, 20), _bits(word, 31, 25)

    result = {"mnemonic": None, "format": None, "fields": {},
              "immediate_value": None, "decode_status": "unsupported"}
    f = result["fields"]
    f["opcode"] = _b(opcode, 7)

    def done(mnemonic, fmt):
        result["mnemonic"], result["format"] = mnemonic, fmt
        result["decode_status"] = "supported"
        return result

    def invalid(fmt):
        result["format"], result["decode_status"] = fmt, "invalid"
        return result

    if opcode == 0b0110011:                       # R-type
        f.update(rd=_b(rd, 5), funct3=_b(funct3, 3), rs1=_b(rs1, 5),
                 rs2=_b(rs2, 5), funct7=_b(funct7, 7))
        op = R_OPS.get((funct3, funct7))
        return done(op, "R") if op else invalid("R")

    if opcode in (0b0010011, 0b0000011, 0b1100111):   # I-type
        f.update(rd=_b(rd, 5), funct3=_b(funct3, 3), rs1=_b(rs1, 5),
                 immediate=_b(_bits(word, 31, 20), 12))
        result["immediate_value"] = _sext(_bits(word, 31, 20), 12)
        if opcode == 0b0010011:
            if funct3 in (1, 5):                  # shifts: imm = funct7 + shamt
                ok = (funct3 == 1 and funct7 == 0x00) or \
                     (funct3 == 5 and funct7 in (0x00, 0x20))
                if not ok:
                    return invalid("I")
                result["immediate_value"] = rs2   # shift amount, 0-31
                name = "slli" if funct3 == 1 else ("srli" if funct7 == 0 else "srai")
                return done(name, "I")
            return done(I_ALU[funct3], "I")       # all other funct3 are valid
        if opcode == 0b0000011:
            op = LOADS.get(funct3)
            return done(op, "I") if op else invalid("I")
        return done("jalr", "I") if funct3 == 0 else invalid("I")

    if opcode == 0b0100011:                       # S-type
        f.update(funct3=_b(funct3, 3), rs1=_b(rs1, 5), rs2=_b(rs2, 5),
                 immediate=_b((funct7 << 5) | rd, 12))
        result["immediate_value"] = _sext((funct7 << 5) | rd, 12)
        op = STORES.get(funct3)
        return done(op, "S") if op else invalid("S")

    if opcode == 0b1100011:                       # B-type
        f.update(funct3=_b(funct3, 3), rs1=_b(rs1, 5), rs2=_b(rs2, 5),
                 immediate=_b((funct7 << 5) | rd, 12))   # raw encoded bits
        imm = (_bits(word, 31, 31) << 12) | (_bits(word, 7, 7) << 11) | \
              (_bits(word, 30, 25) << 5) | (_bits(word, 11, 8) << 1)
        result["immediate_value"] = _sext(imm, 13)       # byte offset
        op = BRANCHES.get(funct3)
        return done(op, "B") if op else invalid("B")

    if opcode in (0b0110111, 0b0010111):          # U-type
        f.update(rd=_b(rd, 5), immediate=_b(_bits(word, 31, 12), 20))
        result["immediate_value"] = _bits(word, 31, 12)  # upper 20 bits
        return done("lui" if opcode == 0b0110111 else "auipc", "U")

    if opcode == 0b1101111:                       # J-type
        f.update(rd=_b(rd, 5), immediate=_b(_bits(word, 31, 12), 20))
        imm = (_bits(word, 31, 31) << 20) | (_bits(word, 19, 12) << 12) | \
              (_bits(word, 20, 20) << 11) | (_bits(word, 30, 21) << 1)
        result["immediate_value"] = _sext(imm, 21)       # byte offset
        return done("jal", "J")

    return result   # anything else: unsupported, opcode only