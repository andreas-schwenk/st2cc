"""
sym.py

Description:
    Symbol definitions.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from st2cc.adr import Address

if TYPE_CHECKING:
    from st2cc.ast import Node


class Symbol:
    """Symbol"""

    def __init__(
        self, scope: str, ident: str, data_type: Node, code: Node, value: Node
    ) -> None:
        self.ident: str = ident
        self.scope = scope  # local | parameter | function | program
        self.data_type: Node = data_type
        self.address: Address = None  # I/O
        self.code: Node = code  # used if scope is "function"
        self.value: Node = value  # used for simulation

    def __str__(self) -> None:
        s = f"SCOPE={self.scope}, ID={self.ident}, TYPE={self.data_type.brackets_str()}"
        if self.address is not None:
            s += f", ADDR={self.address}"
        s += f", VALUE={self.value}"
        if not self.code.is_nil():
            s += ",CODE={\n"
            s += self.code.custom_str(True)
            s += "}"
        return s
