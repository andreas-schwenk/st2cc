"""
ast.py

Description:
    Abstract syntax tree representation via a "Node" data structure.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations
from typing import Dict
from typing import List


from st2c.sym import DataType, Sym


class Node:
    """abstract syntax tree node"""

    def __init__(
        self, ident: str, row: int, col: int, children: List[Node] = None
    ) -> None:
        self.ident: str = ident
        self.row: int = row
        self.col: int = col
        self.dtype: DataType = None
        self.symbols: Dict[str, Sym] = {}
        self.parent: Node = None
        self.children: List[Node] = children if children is not None else []

    def set_parent(self) -> None:
        """sets parent recursively"""
        for c in self.children:
            c.parent = self
            c.set_parent()

    def get_symbol(self, ident: str) -> Sym:
        """get symbol from most inner matching scope"""
        n = self
        while n is not None:
            if ident in n.symbols:
                return n.symbols[ident]
            n = n.parent

    def __str__(self, indentation: int = 0) -> str:
        # TODO: output symbols
        t = str(self.dtype) if self.dtype is not None else ""
        s = f"{self.row}:{self.col}:{self.ident}:<{t}>\n"
        for sym in self.symbols.values():
            s += ("  " * (indentation + 1)) + f"SYMBOL:{sym}\n"
        # if len(self.children) > 0:
        for ci in self.children:
            s += ("  " * (indentation + 1)) + ci.__str__(indentation + 1)
        return s
