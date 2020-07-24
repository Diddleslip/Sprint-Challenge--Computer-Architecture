"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.fl = "00000000"

    def ram_read(self, MAR=0):   # MAR:  _Memory Address Register_ 
        return self.ram[self.pc + MAR] 

    def ram_write(self, MAR, MDR):   # MDR:  _Memory Data Register_
        self.ram[MAR] = MDR
        return self.ram[MAR]

    def load(self, filename):
        """Load a program into memory."""
        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    try:
                        line = line.split("#",1)[0]
                        line = int(line, 2)  # int() is base 10 by default
                        # print("line ", line)
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[0]}")
            sys.exit(1)

        # For now, we've just hardcoded a program:
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
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = "00000100" # L
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = "00000010" # G
            else:
                self.fl = "00000001"  # E
              
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

    def run(self):
        """Run the CPU."""        
        pc = self.pc
        SP = 7
        running = True

        while running:
            inst = self.ram[pc]


            if inst == 130:  # LDI
                reg_num = self.ram[pc + 1]
                value = self.ram[pc + 2]
                self.reg[reg_num] = value

                pc += 3

            elif inst == 162:  # MUL
                self.alu("MUL", self.ram[pc + 1], self.ram[pc + 2])

                pc += 3

            elif inst == 160:  # ADD
                self.alu("ADD", self.ram[pc + 1], self.ram[pc + 2])

                pc += 3

            elif inst == 167:  # CMP
                self.alu("CMP", self.ram[pc + 1], self.ram[pc + 2])

                pc += 3     

            elif inst == 85:  # JEQ
                if self.fl == "00000001":
                    pc = self.reg[self.ram_read(pc + 1)]
                else: 
                    pc += 2

            elif  inst == 84:  # JMP
                pc = self.reg[self.ram_read(pc + 1)]

            elif inst == 86:  # JNE
                if self.fl != "00000001":
                    pc = self.reg[self.ram_read(pc + 1)]
                else:
                    pc += 2

            elif inst == 69:  # PUSH
                # decrement stack pointer
                self.reg[SP] -= 1

                self.reg[SP] &= 0xff  # keep R7 in the range 00-FF

                # get self.reg value
                reg_num = self.ram[pc + 1]
                value = self.reg[reg_num]

                # Store in self.ram
                address_to_push_to = self.reg[SP]
                self.ram[address_to_push_to] = value
                print("In pushing ", value)
                pc += 2

            elif inst == 70:  # POP
                # Get value from RAM
                address_to_pop_from = self.reg[SP]
                value = self.ram[address_to_pop_from]

                # Store in the given self.reg
                reg_num = self.ram[pc + 1]
                self.reg[reg_num] = value

                # Increment SP
                self.reg[SP] += 1
                print("In POPPING ", value)

                pc += 2

            elif inst == 80:  # CALL
                # Get address of the next instruction
                return_addr = pc + 2

                # Push that on the stack
                self.reg[SP] -= 1
                address_to_push_to = self.reg[SP]
                self.ram[address_to_push_to] = return_addr

                # Set the PC to the subroutine address
                reg_num = self.ram[pc + 1]
                subroutine_addr = self.reg[reg_num]

                pc = subroutine_addr

            elif inst == 17: # RET
                # Get return address from the top of the stack
                address_to_pop_from = self.reg[SP]
                return_addr = self.ram[address_to_pop_from]
                self.reg[SP] += 1

                # Set the PC to the return address
                pc = return_addr

            elif inst == 71:  # PRN
                reg = self.ram[pc + 1]
                print("Print method in CPU: ",self.reg[reg])

                pc += 2

            elif inst == 1: # HLT
                running = False

            else:
                print(f"Unknown instruction {inst}")

if __name__ == "__main__": 
    import sys
    from cpu import *

    cpu = CPU()

    cpu.load("sctest.ls8")
    cpu.run()
        
    # numb = "01010100"
    # print("this is numb ",int(numb, 2))