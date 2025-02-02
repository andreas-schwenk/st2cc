"""
lex.py

Description:
    Lexical analyzer / scanner. Divides the input source code into tokens.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from enum import Enum
from typing import List
import sys

from st2cc.lec import KEYWORDS, DELIMITERS, DELIMITERS2
from st2cc.ast import Node


class TokenType(Enum):
    """Type of token"""

    UNKNOWN = 0
    KEYWORD = 1
    IDENT = 2
    STR = 3
    INT = 4
    REAL = 5
    DELIMITER = 6
    END = 7
    ADDR = 8


class Token:
    """Token for lexical analysis"""

    def __init__(self, ident: str = "", row: int = -1, col: int = -1) -> None:
        self.ident: str = ident
        self.row: int = row
        self.col: int = col
        self.type: TokenType = TokenType.UNKNOWN

    def __str__(self) -> str:
        return f"'{self.ident}',{self.row},{self.col},{self.type}"


class Lexer:
    """Lexical analyses"""

    def __init__(self, src: str) -> None:
        self.src: str = src
        self.pos: int = 0
        self.row: int = 1
        self.col: int = 1
        self.token = None

    def expect(self, t: TokenType, ident="") -> Node:
        """expects a given token, or end compilation"""
        if self.token.type != t or (len(ident) > 0 and self.token.ident != ident):
            e = str(t)  # TODO: improve
            if len(ident) > 0:
                e += f":'{ident}'"
            self.error(f"Expected {e}")
        n = Node(self.token.ident, [], self.token.row, self.token.col)
        self.next()
        return n

    def peek(self, t: TokenType, ident: str = "") -> bool:
        """checks for the requested token w/o consuming it"""
        return self.token.type == t and (len(ident) == 0 or self.token.ident == ident)

    def peek_list(self, t: TokenType, ident_list: List[str]) -> bool:
        """checks for the requested tokens w/o consuming it"""
        return self.token.type == t and self.token.ident in ident_list

    def node(self, ident: str, children: List[Node] = None) -> Node:
        """Creates an AST node at the current position"""
        if children is None:
            children = []
        return Node(ident, children, self.token.row, self.token.col)

    def is_end(self):
        """is end?"""
        return self.token.type == TokenType.END

    def next(self) -> None:
        """sets self.token to the next input token"""
        # skip whitespaces and comments
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            if ch in [" ", "\n", "\t"]:
                match ch:
                    case " ":
                        self.col += 1
                    case "\t":
                        self.col += 4
                    case "\n":
                        self.row += 1
                        self.col = 1
                self.pos += 1
            elif (
                ch == "/"
                and self.pos + 1 < len(self.src)
                and self.src[self.pos + 1] == "/"
            ):
                # single line comment
                self.pos += 2
                self.col += 2
                while self.pos < len(self.src) and self.src[self.pos] != "\n":
                    self.pos += 1
                    self.col += 1
            elif (
                ch == "("
                and self.pos + 1 < len(self.src)
                and self.src[self.pos + 1] == "*"
            ):
                # multi line comment
                self.pos += 2
                self.col += 2
                while self.pos < len(self.src) + 1 and not (
                    self.src[self.pos] == "*" and self.src[self.pos + 1] == ")"
                ):
                    self.pos += 1
                    match self.src[self.pos]:
                        case " ":
                            self.col += 1
                        case "\t":
                            self.col += 4
                        case "\n":
                            self.row += 1
                            self.col = 1
                        case _:
                            self.col += 1
                if (
                    self.pos < len(self.src) + 1
                    and self.src[self.pos] == "*"
                    and self.src[self.pos + 1] == ")"
                ):
                    self.pos += 2
                    self.col += 2
                ch = self.src[self.pos]
            else:
                break
        # create a new token
        self.token = Token("", self.row, self.col)
        # end?
        if self.pos >= len(self.src):
            self.token.type = TokenType.END
            return
        # identifier or keyword
        self.token.type = TokenType.IDENT
        i = 0
        while self.pos < len(self.src):
            a = self.src[self.pos].isalpha()
            d = i > 0 and self.src[self.pos].isdigit()
            u = self.src[self.pos] == "_"
            if not (a or d or u):
                break
            self.token.ident += self.src[self.pos].lower()
            self.pos += 1
            self.col += 1
            i += 1
        if self.token.ident in KEYWORDS:
            self.token.type = TokenType.KEYWORD
        if len(self.token.ident) > 0:
            return
        # address = "%" ("I"|"Q") ["X"|"B"|"W"|"D"] INT { "." INT };
        self.token.type = TokenType.ADDR
        if self.src[self.pos] == "%":
            self.token.ident += "%"
            self.pos += 1
            self.col += 1
            if self.pos < len(self.src) and self.src[self.pos] in ["I", "Q"]:
                self.token.ident += self.src[self.pos]
                self.pos += 1
                self.col += 1
                if self.pos < len(self.src) and self.src[self.pos] in [
                    "X",
                    "B",
                    "W",
                    "D",
                ]:
                    self.token.ident += self.src[self.pos]
                    self.pos += 1
                    self.col += 1
                while self.pos < len(self.src) and self.src[self.pos].isdigit():
                    self.token.ident += self.src[self.pos]
                    self.pos += 1
                    self.col += 1
                while self.src[self.pos] == ".":
                    self.token.ident += self.src[self.pos]
                    self.pos += 1
                    self.col += 1
                    while self.pos < len(self.src) and self.src[self.pos].isdigit():
                        self.token.ident += self.src[self.pos]
                        self.pos += 1
                        self.col += 1
        if len(self.token.ident) > 0:
            return
        # integer literal (TODO: exact implementation)
        self.token.type = TokenType.INT
        while self.pos < len(self.src):
            if not self.src[self.pos].isdigit():
                break
            self.token.ident += self.src[self.pos].lower()
            self.pos += 1
            self.col += 1
        if self.token.ident in KEYWORDS:
            self.token.type = TokenType.KEYWORD
        if len(self.token.ident) > 0:
            return
        # delimiter
        self.token.type = TokenType.DELIMITER
        ch = self.src[self.pos]
        if self.src[self.pos] in DELIMITERS:
            self.token.ident += self.src[self.pos]
            self.pos += 1
            self.col += 1
            if (
                self.pos < len(self.src)
                and self.token.ident in DELIMITERS2
                and self.src[self.pos] in DELIMITERS2[self.token.ident]
            ):
                self.token.ident += self.src[self.pos]
                self.pos += 1
                self.col += 1
        if len(self.token.ident) > 0:
            return
        # default: error
        self.error(f"Unknown character '{self.src[self.pos]}'")

    def error(self, msg):
        """exit with error"""
        print(f"ERROR:{self.row}:{self.col}: {msg}")
        sys.exit(-1)
