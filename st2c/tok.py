"""
Token for lexical analysis
"""

from enum import Enum


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


class Token:
    """Token for lexical analysis"""

    def __init__(self, ident: str = "", row: int = -1, col: int = -1) -> None:
        self.ident: str = ident
        self.row: int = row
        self.col: int = col
        self.type: TokenType = TokenType.UNKNOWN

    def __str__(self) -> str:
        return f"'{self.ident}',{self.row},{self.col},{self.type}"
