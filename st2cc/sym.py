"""
sym.py

Description:
    Data types and symbol definitions.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations

from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from st2cc.ast import Node


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

    @staticmethod
    def compare(u: DataType, v: DataType) -> bool:
        """compares two data types"""
        if u.base != v.base:
            return False
        if u.pointer != v.pointer:
            return False
        if u.array_length != v.array_length:
            return False
        if u.array_first_idx != v.array_first_idx:
            return False
        return True

    def __str__(self) -> str:
        return f"{self.base}"  # TODO: other attributes


class AddressDirection:
    """I/O direction"""

    INPUT = 0
    OUTPUT = 1


class Address:
    """Address for I/O"""

    def __init__(self) -> None:
        self.dir: AddressDirection = AddressDirection.INPUT
        self.bits: int = 1
        self.pos: List[int] = [0]

    @staticmethod
    def compare(u: Address, v: Address, cmp_only_pos_0: bool = False) -> bool:
        """compares two addresses"""
        if u.dir != v.dir:
            return False
        if u.bits != v.bits:
            return False
        if cmp_only_pos_0 and u.pos[:1] != v.pos[:1]:
            return False
        if not cmp_only_pos_0 and u.pos != v.pos:
            return False
        return True

    def get_num_bytes(self) -> int:
        """returns the number of bytes"""
        return self.bits // 8

    def get_byte_pos(self) -> int:
        """returns the position of the first byte"""
        if len(self.pos == 0):
            return 0
        return max(1, self.get_num_bytes()) * self.pos[0]

    def __str__(self) -> str:
        s = ""
        match self.dir:
            case AddressDirection.INPUT:
                s += "I"
            case AddressDirection.OUTPUT:
                s += "Q"
        s += {1: "X", 8: "B", 16: "W", 32: "D"}.get(self.bits)
        s += ".".join(map(str, self.pos))
        return s


class Sym:
    """Symbol"""

    def __init__(self, ident="", data_type: DataType = None) -> None:
        self.ident: str = ident
        self.data_type: DataType = data_type
        self.address: Address = None
        self.value: Node = None

        # TODO: reference to AST (e.g. for a function)

    def __str__(self) -> None:
        s = f"{self.ident}:{self.data_type}"
        if self.address is not None:
            s += f":ADDR={self.address}:VALUE={self.value}"
        return s
