"""CPU functionality."""

import sys
import time

HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
LDI = 0b10000010
PRN = 0b01000111
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
IRET = 0b00010011
CMP = 0b10100111
JMP = 0b01010100
JLT = 0b01011000
JNE = 0b01010110
JEQ = 0b01010101
NOP = 0b00000000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.fl = 0b00000000
        self.MAR = None
        self.MDR = None
        self.branchtable = {
            ADD: self.add,
            MUL: self.mul,
            LDI: self.ldi,
            PRN: self.prn,
            POP: self.pop,
            PUSH: self.push,
            CALL: self.call,
            RET: self.ret,
            ST: self.st,
            IRET: self.iret,
            CMP: self.cmp,
            JMP: self.jmp,
            JLT: self.jlt,
            JNE: self.jne,
            JEQ: self.jeq,
            NOP: self.nop
        }


    def ram_read(self, address):
        self.MAR = address
        self.MDR = self.ram[self.MAR]
        return self.MDR

    def ram_write(self, address, value):
        self.MAR = address
        self.MDR = value
        self.ram[self.MAR] = self.MDR


    def load(self, args):
        """Load a program into memory."""

        address = 0
        program = []
        if(len(args) == 2):
            with open(args[1]) as f:
                for line in f:
                    line = line.split("#")[0].strip()

                    if line != "":
                        program.append(int(line, 2))
        else:
            print("Please give 2 valid arguments")
        
        for line in program:
            self.ram[address] = line
            address += 1

    ## ALU Operations handler

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")


    ### Reg Operations

    def ldi(self, req_reg, value):
        self.reg[req_reg] = value
        self.pc += 3

    def prn(self, reg_a, reg_b):
        print(self.reg[reg_a])
        self.pc += 2

    ### ALU Operations

    def add(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def sub(self, reg_a, reg_b):
        self.alu("SUB", reg_a, reg_b)
        self.pc += 3

    def mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)
        self.pc += 3

    def div(self, reg_a, reg_b):
        self.alu("DIV", reg_a, reg_b)
        self.pc += 3

    def mod(self, reg_a, reg_b):
        self.alu("MOD", reg_a, reg_b)
        self.pc += 3

    def cmp(self, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    ### System Stack Operations

    def pop(self, reg_a, reg_b):
        value = self.ram[self.reg[7]]
        self.reg[reg_a] = value
        if self.reg[7] != 0xFF:
            self.reg[7] += 1
        self.pc += 2

    def push(self, reg_a, reg_b):
        self.reg[7] -= 1
        value = self.reg[reg_a]
        self.ram_write(self.reg[7], value)
        self.pc += 2

    def call(self, reg_a, reg_b):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.pc + 2)
        self.pc = self.reg[reg_a]


    def ret(self, reg_a, reg_b):
        stack_value = self.ram[self.reg[7]]
        self.pc = stack_value

    def st(self, reg_a, reg_b):
        self.ram[self.reg[reg_a]] = self.reg[reg_b]

    def iret(self, reg_a, reg_b):
        for i in range(6, -1, -1):
            self.pop(i, reg_b)
        self.fl = self.ram[self.reg[7]]
        self.reg[7] += 1
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1

    def jmp(self, reg_a, reg_b):
        self.pc = self.reg[reg_a]

    def jlt(self, reg_a, reg_b):
        if (self.fl >> 2 & 0b00000001) == 1:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2

    def jne(self, reg_a, reg_b):
        if (self.fl & 0b00000001) == 0:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2

    def jeq(self, reg_a, reg_b):
        if (self.fl & 0b00000001) == 1:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2

    def nop(self, reg_a, reg_b):
        pass


    ## Processing 

    def run(self):
        """Run the CPU."""
        IR = None 
        running = True

        interrupt_start_time = time.perf_counter()

        while running:

            time_checkpoint = time.perf_counter()

            if time_checkpoint - interrupt_start_time >= 1:
                self.reg[6] = self.reg[6]
                interrupt_start_time = time_checkpoint
            
            masked_interrupts = self.reg[5] & self.reg[6]

            for i in range(8):
                interrupt_happened = ((masked_interrupts >> i) & 1) == 1

                if interrupt_happened:
                    self.reg[6] = self.reg[6] & int(
                        '1' * (7 - i) + '0' + '1' * (i), 2)

                    self.reg[7] -= 1
                    self.ram_write(self.reg[7], self.pc)

                    self.reg[7] -= 1
                    self.ram_write(self.reg[7], self.fl)

                    self.fl = 0
                    for j in range(7):
                        self.push(j)
                        self.reg[j] = 0
                    interrupt_vector = 0xF8 + i
                    self.pc = self.ram[interrupt_vector]

            IR = self.ram_read(self.pc)
            after_op_1 = self.ram_read(self.pc+1)
            after_op_2 = self.ram_read(self.pc+2)

            if IR == HLT:
                running = False
                break

            elif IR in self.branchtable:
                self.branchtable[IR](after_op_1, after_op_2)
            
            else:
                print(f"Invalid instruction {IR}")
                sys.exit(1)


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()