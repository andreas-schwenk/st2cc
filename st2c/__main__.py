#!/usr/bin/env python3

"""
st2c.py

A Structured Text (ST) to C Transpiler.

Installation:
    pip install st2c

Dependencies:
    No external dependencies are required, but Python version 3.10 or higher
    is necessary.

Usage:
    python st2c.py [OPTIONS] <input_file>

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
    python st2c.py example.st

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations

from st2c.lex import Lexer
from st2c.par import Parser
from st2c.sem import SemanticAnalysis


def main():
    """main"""

    st_src: str = ""
    with open("examples/example.st", encoding="utf-8") as f:
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
    print("--------")
    print(str(program))
    print("--------")

    sem = SemanticAnalysis(program)
    sem.run()

    print("--------")
    print(str(program))
    print("--------")


if __name__ == "__main__":
    main()
