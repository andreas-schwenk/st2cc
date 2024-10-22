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


class Sym:
    """Symbol"""

    def __init__(self, ident="", data_type: Node = None) -> None:
        # TODO: scope: param, local, function, ...
        # TODO: reference to AST (e.g. for a function)
        self.ident: str = ident
        self.data_type: Node = data_type
        self.address: Address = None
        self.value: Node = None

    def __str__(self) -> None:
        s = f"{self.ident}, {self.data_type.brackets_str()}"
        if self.address is not None:
            s += f", ADDR={self.address}"
        s += f", VALUE={self.value}"
        return s
