"""CPU functionality."""

import sys
import time

ADD = 0b10100000
AND = 0B10101000
CALL = 0b01010000
CMP = 0b10100111
HLT = 0b00000001
IRET = 0b00010011
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
LD = 0b10000011
LDI = 0b10000010
MOD = 0b10100100
MUL = 0b10100010
NOT = 0b01101001
OR = 0b10101010
POP = 0b01000110
PRN = 0b01000111
PRA = 0b01001000
PUSH = 0b01000101
RET = 0b00010001
SHL = 0b10101100
SHR = 0b10101101
ST = 0b10000100
XOR = 0b10101011
ST = 0b10000100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
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
                    line = line.split("#")[0]

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

    def mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)
        self.pc += 3

    def div(self, reg_a, reg_b):
        self.alu("DIV", reg_a, reg_b)
        self.pc += 3

    def mod(self, reg_a, reg_b):
        self.alu("MOD", reg_a, reg_b)
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
        return_address = self.pc + 2
        self.ram_write(self.reg[7], return_address)
        self.pc = self.reg[reg_a]


    def ret(self, reg_a, reg_b):
        stack_value = self.ram[self.reg[7]]
        self.pc = stack_value

    def st(self, reg_a, reg_b):
        self.ram[self.reg[reg_a]] = self.reg[reg_b]

    ## Processing 

    def run(self):
        """Run the CPU."""
        IR = None 
        running = True

        interrupt_start_time = time.perf_counter()

        while running:

            time_checkpoint = time.perf_counter()

            if time_checkpoint - interrupt_start_time >= 1:
                self.reg[6] = self.reg[6] | 0b00000001
                interrupt_start_time = time_checkpoint

            IR = self.ram_read(self.pc)
            after_op_1 = self.ram_read(self.pc+1)
            after_op_2 = self.ram_read(self.pc+2)

            if IR == HLT:
                running = False
                break

            elif IR in self.branchtable:
                self.branchtable[IR](after_op_1, after_op_2)
            
            else:
                sys.exit()


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