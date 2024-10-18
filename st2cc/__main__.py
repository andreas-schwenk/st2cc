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

    --cfg CONFIG_FILE.toml
        Provides a config file.

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
import tomllib
import os

from st2cc.lex import Lexer
from st2cc.par import Parser
from st2cc.sem import SemanticAnalysis
from st2cc.gen import CodeGenerator
from st2cc.int import Interpreter


def main():
    """main"""

    # parse args
    parser = argparse.ArgumentParser(
        description="st2cc -- Structured Text To C Compiler and interpreter by Andreas Schwenk"
    )
    parser.add_argument("-i", action="store_true", help="Interpret the input file.")
    parser.add_argument("-v", action="store_true", help="Enable verbose mode.")
    parser.add_argument(
        "--cfg",
        metavar="FILE",
        help="Provide a TOML config file.",
    )
    parser.add_argument("input_file", metavar="FILE", help="The input file to process.")
    args = parser.parse_args()

    # extract args
    interpret = args.i
    verbose = args.v
    cfg_file_path = args.cfg
    input_file_path = args.input_file
    output_file_path = os.path.splitext(input_file_path)[0] + ".c"

    config = {}
    if len(cfg_file_path) > 0:
        with open("examples/example-cfg.toml", "rb") as f:
            config = tomllib.load(f)

    st_src: str = ""
    with open(input_file_path, encoding="utf-8") as f:
        st_src = f.read()

    lexer = Lexer(st_src)

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

    if interpret:
        interpreter = Interpreter(program, config)
        interpreter.run()

    gen = CodeGenerator(program, config, verbose)
    c_src = gen.run()

    with open(output_file_path, mode="w", encoding="utf-8") as f:
        f.write(c_src)


if __name__ == "__main__":
    main()
