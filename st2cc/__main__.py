#!/usr/bin/env python3

"""
st2cc.py

A Structured Text (ST) to C Compiler.

Installation:
    pip install st2cc

Dependencies:
    No external dependencies are required, but Python version 3.10 or higher
    is necessary.

Usage:
    python st2cc.py [OPTIONS] <input_file>

Options:
    -h, --help
        Shows the help message and exists.

    -i, --interpret
        Interprets the program in the input file.

    -v, --verbose
        Enables the verbose mode for detailed logging.

    --version
        Displays the version number.

Description:
    This script acts as a compiler for programs written in the Structured Text 
    (ST) programming language, converting them into C code by default. 
    The generated output files have the .c extension, which replaces the 
    original .st extension of the input files.

Examples:
    python st2cc.py example.st

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations
import argparse

from st2cc.lex import Lexer
from st2cc.par import Parser
from st2cc.sem import SemanticAnalysis
from st2cc.gen import CodeGenerator
from st2cc.int import Interpreter, TestData


def main():
    """main"""

    # parse args
    parser = argparse.ArgumentParser(
        description="st2cc -- Structured Text To C Compiler and interpreter by Andreas Schwenk"
    )
    parser.add_argument("-i", action="store_true", help="Interpret the input file.")
    parser.add_argument("-v", action="store_true", help="Enable verbose mode.")
    parser.add_argument(
        "--addr",
        metavar="FILE",
        help="Provide a CSV config file for physical addresses.",
    )
    parser.add_argument(
        "--test",
        metavar="FILE",
        help="Provide a CSV config file for test values (Only useful with -i option).",
    )
    parser.add_argument("input_file", metavar="FILE", help="The input file to process.")
    args = parser.parse_args()

    # extract args
    interpret = args.i
    verbose = args.v
    addr_file_path = args.addr  # TODO
    test_file_path = args.test
    input_file_path = args.input_file

    # TODO: move code
    # with open("examples/example-io.csv", mode="r", encoding="utf-8") as f:
    #     r = csv.reader(f)
    #     for row in r:
    #         if row and not row[0].startswith("#"):
    #             print(row)

    st_src: str = ""
    with open(input_file_path, encoding="utf-8") as f:
        st_src = f.read()
        f.close()

    lexer = Lexer(st_src)
    # lexer.next()
    # while lexer.token.type != TokenType.END:
    #    print(lexer.token)
    #    lexer.next()
    # sys.exit(0)

    parser = Parser(lexer)
    program = parser.parse()
    if verbose:
        print("-------- parser output: ------")
        print(str(program))
        print("--------")

    sem = SemanticAnalysis(program)
    sem.run()
    if verbose:
        print("-------- SEMANTIC ANALYSIS output: -----")
        print(str(program))
        print("--------")

    gen = CodeGenerator(program)
    gen.run()

    if interpret:
        test_data = TestData()
        test_data.read(test_file_path)
        interpreter = Interpreter(program, test_data)
        interpreter.run()


if __name__ == "__main__":
    main()
