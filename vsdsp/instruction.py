from struct import unpack


class Arg:
    """Extract integer argument value from opcode."""
    def __init__(self, opcode, offs, size):
        self.value = (opcode >> offs) & ((1 << size) - 1)

    def __str__(self):
        return hex(self.value)


class ArgAddr(Arg):
    """Addressing using index register, optionally with postmodification."""
    def __init__(self, arg_addr_reg, arg_addr_mod):
        self.reg = arg_addr_reg
        self.mod = arg_addr_mod

    def __str__(self):
        return '%s%s' % (str(self.reg), str(self.mod), )


class ArgAddrReg(Arg):
    """Addressing using index register."""
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 3)

    def __str__(self):
        return "(I%s)" % str(self.value)


class AddrPostMod(Arg):
    """Postmodification of index register."""
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 4)
        if self.value > 7:
# get signed value (4bit)
            self.value = self.value - 16

    def __str__(self):
        if self.value == 0:
            return ""
        if self.value == -8:
            raise NotImplementedError("AddrPostMod value %d" % self.value)
        return "%+d" % self.value


class AddrPostModShort(AddrPostMod):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 1)
        self.value = self.value << 3


class ArgConst(Arg):
    def __init__(self, opcode, offs, size):
        Arg.__init__(self, opcode, offs, size)


class ArgReg16(Arg):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 3)

    def __str__(self):
        return {
                0: "A0",
                1: "A1",
                2: "B0",
                3: "B1",
                4: "C0",
                5: "C1",
                6: "D0",
                7: "D1",
                }[self.value]


class ArgRegWide(Arg):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 3)

    def __str__(self):
        return {
                0: "Reserver A",
                1: "A",
                2: "Reserver B",
                3: "B",
                4: "Reserver C",
                5: "C",
                6: "Reserver D",
                7: "D",
                }[self.value]


class ArgRegALUOp(Arg):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 4)

    def __str__(self):
        return {
                0: "A0",
                1: "A1",
                2: "B0",
                3: "B1",
                4: "C0",
                5: "C1",
                6: "D0",
                7: "D1",
                8: "NULL",
                9: "ONES",
                10: "Reserver result",
                11: "P",
                12: "A",
                13: "B",
                14: "C",
                15: "D",
                }[self.value]

    def wide(self):
        return self.value >= 11 and self.value <= 15


class ArgRegFull(Arg):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 6)

    def __str__(self):
        return {
                0b000000: "A0",
                0b000001: "A1",
                0b000010: "B0",
                0b000011: "B1",
                0b000100: "C0",
                0b000101: "C1",
                0b000110: "D0",
                0b000111: "D1",
                0b001000: "LR0",
                0b001001: "LR1",
                0b001010: "MR0",
                0b001011: "MR1",
                0b001100: "NULL",
                0b001101: "LC",
                0b001110: "LS",
                0b001111: "LE",
                0b010000: "I0",
                0b010001: "I1",
                0b010010: "I2",
                0b010011: "I3",
                0b010100: "I4",
                0b010101: "I5",
                0b010110: "I6",
                0b010111: "I7",
                0b011000: "I8",
                0b011001: "I9",
                0b011010: "I10",
                0b011011: "I11",
                0b011100: "I12",
                0b011101: "I13",
                0b011110: "I14",
                0b011111: "I15",
                0b100000: "A2",
                0b100001: "B2",
                0b100010: "C2",
                0b100011: "D2",
                0b100100: "NOP",
                0b100101: "Reserver 0b100101",
                0b100110: "Reserver 0b100110",
                0b100111: "Reserver 0b100111",
                0b101000: "Reserver 0b101000",
                0b101001: "Reserver 0b101001",
                0b101010: "Reserver 0b101010",
                0b101011: "Reserver 0b101011",
                0b101100: "Reserver 0b101100",
                0b101101: "Reserver 0b101101",
                0b101110: "Reserver 0b101110",
                0b101111: "Reserver 0b101111",
                0b110000: "Reserver 0b110000",
                0b110001: "Reserver 0b110001",
                0b110010: "Reserver 0b110010",
                0b110011: "Reserver 0b110011",
                0b110100: "Reserver 0b110100",
                0b110101: "Reserver 0b110101",
                0b110110: "Reserver 0b110110",
                0b110111: "Reserver 0b110111",
                0b111000: "Reserver 0b111000",
                0b111001: "Reserver 0b111001",
                0b111010: "Reserver 0b111010",
                0b111011: "Reserver 0b111011",
                0b111100: "Reserver 0b111100",
                0b111101: "Reserver 0b111101",
                0b111110: "IPR0",
                0b111111: "IPR1",
                }[self.value]


class Instruction:
    def __init__(self, name, args=None, parallel=None):
        """name - instruction mnemonic
        args - instruction arguments
        parallel - follow up parallel instruction"""
        self.name = name
        self.args = args
        self.parallel = parallel

    def __str__(self):
        s = self.name
        if self.args:
            s += "\t" + ", ".join([str(s) for s in self.args])
        if self.parallel:
            s += ";\t" + str(self.parallel)
        return s


class OpLDC(Instruction):
    """LDC instruction."""
    def __init__(self, opcode):
        self.opcode = opcode
        args = (
                ArgConst(opcode, 6, 5*4+3),
                ArgRegFull(opcode, 0),
                )
        Instruction.__init__(self, "LDC", args)


class OpControl(Instruction):
    """Class of control instructions (J, CALL, RET, ...)."""
    def __init__(self, opcode):
        self.opcode = opcode

    def __str__(self):
        raise NotImplementedError("%x" % self.opcode)


class OpParallel(Instruction):
    """Class of instructions with parallel move."""
    def __init__(self, opcode):
        self.opcode = opcode
        op = (opcode >> 28) & 0xf
        if op == 0x3:
            return self._init_double_full_move()
        if op == 0xf:
            return self._init_singlearg()
        if op == 0x5 or op == 0x7:
            return self._init_mac(op)
        self._init_aritm(op)

    def _init_aritm(self, op):
        arg1 = ArgRegALUOp(self.opcode, 24)
        arg2 = ArgRegALUOp(self.opcode, 20)
        if arg1.wide() or arg2.wide():
            arg3 = ArgRegWide(self.opcode, 17)
        else:
            arg3 = ArgReg16(self.opcode, 17)
        name = {
                4: 'ADD',
                6: 'SUB',
                8: 'ADDC',
                9: 'SUBC',
                11: 'AND',
                12: 'OR',
                13: 'XOR',
                } [op]
        move = self._parallel_move()
        Instruction.__init__(self, name, (arg1, arg2, arg3, ), move)

    def _init_double_full_move(self):
        mov1 = self._full_move(14, 'X')
        mov2 = self._full_move(0, 'Y')
        mov2 = Instruction(mov2[0], mov2[1:])
        Instruction.__init__(self, mov1[0], mov1[1:], mov2)

    def _init_mac(self, op):
        raise NotImplementedError()

    def _init_mul(self):
        _format = {
                0: 'SS',
                1: 'SU',
                2: 'US',
                3: 'UU',
                }  [(self.opcode >> 23) & 0x3]
        arg1 = ArgReg16(self.opcode, 20)
        arg2 = ArgReg16(self.opcode, 17)
        move = self._parallel_move()
        Instruction.__init__(self, 'MUL' + _format, (arg1, arg2, ), move)

    def _init_singlearg(self):
        subop = (self.opcode >> 24) & 0xf
        if subop == 0x4:
            return Instruction.__init__(self, 'NOP')
        if (subop & 0x0e) == 0xe:
            return self._init_mul()
        name = {
                0: 'ABS',
                1: 'ASR',
                2: 'LSR',
                3: 'LSRC',
                } [subop]
        arg1 = ArgRegALUOp(self.opcode, 20)
        if arg1.wide():
            arg2 = ArgRegWide(self.opcode, 17)
        else:
            arg2 = ArgReg16(self.opcode, 17)
        move = self._parallel_move()
        Instruction.__init__(self, name, (arg1, arg2, ), move)

    def _parallel_move(self):
        if (self.opcode >> 16) & 0x1:
            return self._short_moves()
        else:
            bus = { 0: 'X', 1: 'I!!!', 2: 'Y', }[(self.opcode >> 14) & 3]
            move = self._full_move(0, bus)
            return Instruction(move[0], move[1:])

    def _full_move(self, offs, bus):
        opcode = self.opcode >> offs
        name = { 0: 'LD', 1: 'ST' } [(opcode >> 13) & 1]
        name += bus
        reg_addr = ArgAddr(ArgAddrReg(opcode, 10), AddrPostMod(opcode, 6))
        reg = ArgRegFull(opcode, 0)
        return (name, reg_addr, reg)

    def _short_move(self, offs, mov2=None):
        opcode = self.opcode >> offs
        name = { 0: 'LD', 1: 'ST' } [(opcode >> 7) & 1]
        name += 'X' if offs else 'Y'
        reg_addr = ArgAddr(ArgAddrReg(opcode, 4), AddrPostModShort(opcode, 3))
        reg = ArgReg16(opcode, 0)
        return Instruction(name, (reg_addr, reg, ), mov2)

    def _short_moves(self):
        return self._short_move(8, self._short_move(0))

    def __str__(self):
        if not hasattr(self, 'name'):
            raise NotImplementedError(hex(self.opcode))
            return "OpParallel " + hex(self.opcode)
        return Instruction.__str__(self)


class Decoder:
    def __init__(self, buf, offs=0):
        """Decode instructions from buffer."""
        self._buf = buf
        self._offs = offs

    def decode(self, n=None):
        instr = []
        if n is None:
            n = divmod(len(self._buf), 4)[0]
        while n:
            opcode = unpack('<I', self._buf[self._offs:self._offs+4])[0]
            self._offs += 4
            n -= 1
            op = (opcode >> 29) & 0xe
            if op == 0:
                instr.append(OpLDC(opcode))
                continue
            op = (opcode >> 28) & 0xf
            if op == 2:
                instr.append(OpControl(opcode))
                continue
            instr.append(OpParallel(opcode))

        return instr
