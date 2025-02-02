# st2cc

<img src="logo.svg?v=5" width="128" height="128"/>

`st2cc` is a Structured Text (ST) to C compiler and interpreter, developed in 2024 by Andreas Schwenk (schwenk@member.fsf.org).

[!CAUTION]
Work in progress: Only basic, trivial examples are currently functional.

# License

GPLv3 (GNU General Public License, Version 3)

# Installation

```bash
pip install st2cc
```

# Usage

```bash
st2cc INPUT_FILE
```

The input file, written in Structured Text (ST), is converted into a C file.

For example: "st2cc text.st" is translated to "text.c"

## Config

TOML file

In part `[test]`, the dot notation of addresses is **not** allowed. Values are specified for entire bytes. Using the bit representation may be more readable (e.g. `0b111` instead of `7`).

If output address values are given, values are asserted.

# Dependencies

No external dependencies are required, but Python version 3.10 or higher
is necessary.

# Example

input: TODO

output: TODO

# Grammar

Formal grammar of ST. Only the implemented parts are listed.

```ebnf
program = "PROGRAM" ID "VAR" variable* "END_VAR" statement* "END_PROGRAM";
variable = ID ":" type ";"
type = "BOOL" | "INT" | "REAL";
statement = if | assignment;
if = "IF" expr "THEN" statement* [ "ELSE" statement* "END_IF" ];
assignment = ID ":=" expr ";";
expr = mul;
mul = unary { "*" unary };
unary = "TRUE" | "FALSE" | REAL | INT | ID;
```

# Developer Information

This project is implemented as a Python package and includes all necessary modules for compiling and transforming Structured Text (ST) code into C code.

### Debugging in VS Code

Debug configurations for Visual Studio Code are available in the `.vscode` directory. These settings allow you to easily set breakpoints, inspect variables, and step through the code.

## Project Structure

The core components of the compiler are located in the `st2cc/` directory. Below is an overview of each file and its purpose:

| File          | Description                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------ |
| `__main__.py` | **Entry Point**: Manages command-line arguments and controls the compilation process.            |
| `ast.py`      | **Abstract Syntax Tree (AST)**: Defines the structure and nodes used to represent the program.   |
| `gen.py`      | **Code Generation**: Generates equivalent C code from the AST.                                   |
| `lex.py`      | **Lexical Analysis**: Scans and tokenizes the source code.                                       |
| `par.py`      | **Parser**: Implements a top-down LL(1) parser with one-token lookahead to analyze syntax.       |
| `sem.py`      | **Semantic Analysis**: Validates data types and builds the symbol table integrated into the AST. |
| `sym.py`      | **Symbol Table and Data Types**: Manages data type definitions and symbol table operations.      |
| `tok.py`      | **Lexer Tokens**: Defines the tokens used during lexical analysis.                               |

TODO

# ST References

## general

- https://en.wikipedia.org/wiki/Structured_text

## Addresses

- https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_operands_addresses.html

## Implementations

- https://github.com/PLC-lang/rusty?tab=readme-ov-file
- https://plc-lang.github.io/rusty/intro_1.html
