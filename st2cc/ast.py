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


from st2cc.sym import DataType, Sym


class Node:
    """abstract syntax tree node"""

    def __init__(
        self, ident: str, row: int, col: int, children: List[Node] = None
    ) -> None:
        self.ident: str = ident
        self.row: int = row
        self.col: int = col
        self.data_type: DataType = None
        self.symbols: Dict[str, Sym] = {}
        self.parent: Node = None
        self.children: List[Node] = children if children is not None else []

    def clone(self) -> Node:
        """clones a node"""
        c = Node(self.ident, self.row, self.col, [])
        c.data_type = self.data_type
        c.symbols = self.symbols
        c.parent = self.parent
        for child in self.children:
            c.children.append(child.clone())
        return c

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

    def __str__(self) -> str:
        return self.custom_str()

    def custom_str(self, show_position: bool = True, indentation: int = 0) -> str:
        """custom stringify"""
        t = str(self.data_type) if self.data_type is not None else ""
        s = ""
        if show_position:
            s += f"{self.row}:{self.col}:"
        s += f"{self.ident}:<{t}>\n"
        for sym in self.symbols.values():
            s += ("  " * (indentation + 1)) + f"SYMBOL:{sym}\n"
        for ci in self.children:
            s += ("  " * (indentation + 1)) + ci.custom_str(
                show_position, indentation + 1
            )
        return s
