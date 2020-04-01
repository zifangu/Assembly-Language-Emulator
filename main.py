#!/usr/bin/env python3
"""
Author: Ivan Gu and Bennett Joyce

This module is an emulator for Ben Eater's SAP-1 computer.

Usage:
    python3 main.py [--trace] [--pause] sap-filename

The --trace flag causes trace output to be printed.
The --pause flag causes the emulator to pause after each instruction is executed.

A program is loaded from a text file named on the command line.
Each line contains a hexadecimal or decimal memory address followed
by a space and then a value expressed in binary, hex, or decimal.
A comment starts with # and continues to the end of the line.
Note: Binary, hex, or decimal numbers follow Python syntax rules

Example input file contents:
# Add numbers
0x00 0b00011110 # LDA 14
0x01 0b00101111 # ADD 15
0x02 0b11100000 # OUT
0x03 0b11110000 # HLT
0x0E 0b00001110 # 14
0x0F 0b00011100 # 28
"""

import sys
import re
import argparse


class Halt(Exception):
    pass


class InvalidInstruction(Exception):
    pass


class SAP1:
    """
    An instance of a Simple-as-Possible-1 computer
    """

    OPCODES = {
        0b0000: 'NOP',
        0b0001: 'LDA',
        0b0010: 'ADD',
        0b0011: 'SUB',
        0b0100: 'STA',
        0b0101: 'OUT',
        0b0110: 'JMP',
        0b0111: 'LDI',
        0b1000: 'JC',
        0b1111: 'HLT'
    }

    def __init__(self):
        """
        Initialize an instance with all registers and memory locations 0
        """
        # These represent the machine registers
        self.memory = [0] * 16
        self.A_register = 0
        self.B_register = 0
        self.PC_register = 0
        self.RAM = 0
        self.MAR = 0
        self.IR = 0
        self.Carry = 0

        # The tuple below can be indexed by an opcode to access a function that executes
        # that opcode
        self.decoder = (self.NOP, self.LDA, self.ADD, self.SUB,
                        self.STA, self.OUT, self.JMP, self.LDI,
                        self.JC, self.UND, self.UND, self.UND,
                        self.UND, self.UND, self.UND, self.HLT)

    def NOP(self):
        """
        Execute a NOP instruction
        :return: None
        """
        pass

    def LDA(self):
        """
        Execute an LDA instruction
        :return: None
        """
        # T3: Load MAR with the address in the right four bits of IR
        self.MAR = self.IR % 16

        # T4: Move the contents of memory at address MAR to the A register
        self.A_register = self.memory[self.MAR]

        # T5: nop
        pass

    def ADD(self):
        """
        Execute an ADD instruction
        :return: None
        """
        # add in A-reg with memory. Load in B-reg
        self.B_register = self.memory[self.IR % 16]
        sum = self.A_register + self.B_register
        self.A_register = sum % 256
        self.Carry = sum // 256

    def SUB(self):
        """
        Execute a SUB instruction
        :return: None
        """
        self.B_register = self.memory[self.IR % 16]
        diff = self.A_register - self.B_register
        self.A_register = diff % 256
        if diff < 0:
            self.Carry = 1
        else:
            self.Carry = 0

    def STA(self):
        """
        Execute an STA instruction
        :return: None
        """

        self.memory[self.IR % 16] = self.A_register


    def JMP(self):
        """
        Execute a JMP instruction
        :return: None
        """
        self.PC_register = self.IR % 16


    def LDI(self):
        """
        Execute an LDI instruction
        :return: None
        """
        self.A_register = self.IR % 16

    def JC(self):
        """
        Execute a JC instruction
        :return: None
        """
        if self.Carry == 1:
            self.PC_register = self.IR % 16

    def OUT(self):
        """
        Execute an OUT instruction
        :return: None
        """
        print('****\n**** OUTPUT: {0:d}  0x{0:04X}  {0:04X}h  0b{0:08b}\n****'.format(self.A_register))

    def HLT(self):
        """
        Execute a HLT instruction
        :return: None
        :raise: Halt exception
        """
        raise Halt('HLT executed when PC is {}'.format(self.PC_register))

    def UND(self):
        """
        Execute an undefined instruction
        :return: None
        :raise: InvalidInstruction exception
        """
        raise InvalidInstruction('Invalid opcode: 0x{0:02x}   0b{0:08b}'.format(self.IR))

    def emulate(self, trace=False, pause =False):
        """
        Run the program loaded in memory
        :param trace: True if machine state to be displayed after each instruction
        :param pause: True if execution for pause until input is entered
        :return: None
        :raise: Halt when a HLT instruction is executed
        """

        try:
            # Fetch-execute cycle
            while True:

                # FETCH PHASE
                if trace:
                    print()
                    print('---- START fetch/decode/execute ----')
                    print(f' PC: {self.PC_register}')

                # T0: Load MAR with the contents of PC
                self.MAR = self.PC_register
                if trace:
                    print(f'MAR: {self.MAR}')

                # T1: Load IR with the contents of memory at the address given in MAR
                self.IR = self.memory[self.MAR]
                if trace:
                    print(f' IR: {self.IR}')

                # T2: Bump the PC up by 1
                self.PC_register = (self.PC_register + 1) % 16
                if trace:
                    print(f' PC: {self.PC_register}')

                # DECODE/EXECUTE PHASE
                # Perform the instruction whose opcode is given by the leftmost four
                # bits of IR
                opcode = self.IR // 16
                if trace:
                    print(f'Opcode: {opcode} - {SAP1.OPCODES[opcode]}')
                self.decoder[opcode]()

                if trace:
                    print()
                    print("Machine State")
                    print(self)

                if pause:
                    input(f"Pause PC = {self.PC_register}: Type RETURN/ENTER to continue")

        except Halt as e:
            if trace:
                print('HLT encountered')
            print(e)

        except InvalidInstruction as e:
            print(e)

    def load(self, filename):
        """
        Load the program from a file
        :param filename:
        :return: None
        :raise: ValueError if file contains a formatting error
        """
        with open(filename) as program_file:
            for line in program_file:
                # Remove any comment part and leading or trailing spaces
                line = re.sub(r'#.*$', '', line).strip()
                if line:
                    addr, value = line.split()
                    # See: https://stackoverflow.com/questions/604240/how-to-parse-hex-or-decimal-int-in-python
                    # See also: https://docs.python.org/3/library/functions.html#int
                    self.memory[int(addr, 0)] = int(value, 0)

    def __str__(self):
        """
        Return a string showing the current machine state
        :return: a str
        """

        # Build a list containing each component of the state
        lines = ["",
                 "   PC:      {0:04b}    0x{0:02X}".format(self.PC_register),
                 "   IR:  {0:08b}  0x{0:04X}".format(self.IR),
                 "    A:  {0:08b}  0x{0:04X}".format(self.A_register),
                 "    B:  {0:08b}  0x{0:04X}".format(self.B_register),
                 "  MAR:  {0:04b}  0x{0:04X}".format(int(self.MAR)),
                 "  RAM:  {0:04b}  0x{0:04X}".format(int(self.RAM)),
                 "Carry:  {0:4b}  0x{0:X}".format(self.Carry),
                 "Memory:"]
        lines.extend(
            ['    {0:04b}: {1:08b}  {1:3d}  0x{1:04X}'.format(addr, value) for addr, value in enumerate(self.memory)])

        # Return a string constructed by joining all the strings in the list
        return '\n    '.join(lines)


def main():
    """
    Load the program in a file named as a command line argument
    :return: None
    """

    ap = argparse.ArgumentParser(prog='sap', description='Simulate execution of a SAP1 program')
    ap.add_argument('filename',
                    metavar='filename',
                    type=str,
                    help='the name of the file containing binary')
    ap.add_argument('-t',
                    '--trace',
                    action='store_true',
                    help='display state after each instruction')
    ap.add_argument('-p',
                    '--pause',
                    action='store_true',
                    help='pause for keyboard input after each instruction excution')

    args = ap.parse_args()
    filename = args.filename
    trace = args.trace
    pause = args.pause

    computer = SAP1()

    print("START")

    try:
        computer.load(args.filename)
        if trace:
            print(f'Load of {filename} complete.')
            print(computer)
            print()

        computer.emulate(trace=trace, pause=pause)

    except FileNotFoundError:
        print("Could not open file {}.".format(filename), file=sys.stderr)

    except ValueError:
        print("Error reading file {}.".format(filename), file=sys.stderr)


if __name__ == '__main__':
    main()
