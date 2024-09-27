# ST2C

<img src="logo.svg?v=3" width="128" height="128"/>

Structured Text (ST) to C Transpiler

Written 2024 by Andreas Schwenk <schwenk@member.fsf.org>

# License

GPLv3 (GNU General Public License, Version 3)

# Installation

```bash
pip install st2c
```

# Usage

```bash
st2c INPUT_FILE
```

The input file, written in Structured Text (ST), is converted into a C file.

For example: "st2c text.st" is translated to "text.c"

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
