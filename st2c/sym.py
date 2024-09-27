"""
Data types and symbols
"""

from enum import Enum


class BaseType(Enum):
    """Base Type"""

    BOOL = 0
    INT = 1
    REAL = 2


class DataType:
    """Data type"""

    def __init__(self, base: BaseType) -> None:
        self.base: BaseType = base
        self.pointer: bool = False
        self.array_length: bool = 1
        self.array_first_idx: int = 1

    def __str__(self) -> str:
        return f"{self.base}"  # TODO: other attributes


class Sym:
    """Symbol"""

    def __init__(self, ident="", data_type: DataType = None) -> None:
        self.ident: str = ident
        self.data_type: DataType = data_type

    def __str__(self) -> None:
        return f"{self.ident}:{self.data_type}"
