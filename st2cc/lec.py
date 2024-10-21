"""
lec.py

Description:
    Lexical constants.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

# set of keywords (lowercase)
KEYWORDS = {
    "and",
    "at",
    "bool",
    "else",
    "end_function",
    "end_if",
    "end_program",
    "end_var",
    "false",
    "function",
    "if",
    "int",
    "or",
    "program",
    "real",
    "then",
    "true",
    "var_input",
    "var",
}

# set of single-character delimiters
DELIMITERS = {":", "*", "+", ";", "(", ")", "<", ">", "=", "-", "/"}

# set of two-character delimiters
DELIMITERS2 = {":": {"="}, "<": {"="}, ">": {"="}, "*": {"*"}}
