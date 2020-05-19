"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.branchtable = {}
        self.branchtable_ops()
        ## main stack register is called the stack pointer => https://books.google.co.uk/books?id=9vaFDwAAQBAJ&pg=PA410&lpg=PA410&dq=CPU+address+0xF3&source=bl&ots=tQs8CNjKFj&sig=ACfU3U19OP1uIiM5HJubkSE5AWn6sAL93A&hl=en&sa=X&ved=2ahUKEwix-rj6jcDpAhX9RBUIHRXCCPAQ6AEwAHoECAcQAQ#v=onepage&q=CPU%20address%200xF3&f=false
        self.stack_pointer = 0xF3

    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, address, value):
        self.ram[address] = value


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


        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


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

    def POP(self, reg_a, reg_b):
        value = self.ram[self.stack_pointer]
        self.reg[reg_a] = value

        # We cannot move past the top of the stack, so once we reach 0xFF, we shouldn't increase the pointer
        if self.stack_pointer != 0xFF:
            self.stack_pointer += 1
        self.pc += 2


    def PUSH(self, reg_a, reg_b):
        # Move stack pointer down, get value from register and insert value onto stack
        self.stack_pointer -= 1
        value = self.reg[reg_a]
        self.ram_write(self.stack_pointer, value)
        self.pc += 2



    def branchtable_ops(self):
        self.branchtable[0b10000010] = self.ldi
        self.branchtable[0b01000111] = self.prn
        self.branchtable[0b10100000] = self.add
        self.branchtable[0b10100010] = self.mul
        self.branchtable[0b01000110] = self.POP
        self.branchtable[0b01000101] = self.PUSH


    def run(self):
        """Run the CPU."""
        IR = None 
        running = True

        while running:
            IR = self.ram_read(self.pc)
            after_op_1 = self.ram_read(self.pc+1)
            after_op_2 = self.ram_read(self.pc+2)


            ## HLT => exit loop 0b00000001 = 1
            if IR == 0b00000001:
                running = False
                break

            ## LDI => give specified register a specified value 0b10000010 = 130
            elif IR in self.branchtable:
                self.branchtable[IR](after_op_1, after_op_2)
            
            ## if all else fails
            else:
                sys.exit()

