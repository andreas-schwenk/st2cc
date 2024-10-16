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
import sys

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
        self.direction: AddressDirection = AddressDirection.INPUT
        self.bits: int = 1
        self.position: List[int] = [0]

    def get_num_bytes(self) -> int:
        """returns the number of bytes"""
        return self.bits // 8

    def get_byte_pos(self) -> int:
        """returns the position of the first byte"""
        if len(self.position == 0):
            return 0
        b = 0
        match self.bits:
            case 1:
                b = self.position[0]
            case 8:
                b = self.position[0]
            case 16:
                b = 2 * self.position[0]
            case 32:
                b = 4 * self.position[0]
        return b

    def parse(self, data) -> None:
        """parses the address"""
        # direction
        if data.startswith("I"):
            self.direction = AddressDirection.INPUT
            data = data[1:]
        elif data.startswith("Q"):
            self.direction = AddressDirection.OUTPUT
            data = data[1:]
        else:
            print("unexpected error while parsing the address")  # TODO
            sys.exit(-1)
        # number of bits
        if data.startswith("X"):
            self.bits = 1
            data = data[1:]
        elif data.startswith("B"):
            self.bits = 8
            data = data[1:]
        elif data.startswith("W"):
            self.bits = 16
            data = data[1:]
        elif data.startswith("D"):
            self.bits = 32
            data = data[1:]
        # position
        self.position = list(map(int, data.split(".")))

    def __str__(self) -> str:
        s = ""
        match self.direction:
            case AddressDirection.INPUT:
                s += "I"
            case AddressDirection.OUTPUT:
                s += "Q"
        s += {1: "X", 8: "B", 16: "W", 32: "D"}.get(self.bits)
        s += ".".join(map(str, self.position))
        return s


class Sym:
    """Symbol"""

    def __init__(self, ident="", data_type: DataType = None) -> None:
        self.ident: str = ident
        self.data_type: DataType = data_type
        self.address: Address = None
        self.value: Node = None

    def __str__(self) -> None:
        s = f"{self.ident}:{self.data_type}"
        if self.address is not None:
            s += f":ADDR={self.address}:VALUE={self.value}"
        return s
