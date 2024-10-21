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
from typing import Dict, List


from st2cc.sym import DataType, Sym, BaseType


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

    @staticmethod
    def create_const_bool(value: bool) -> Node:
        """creates a node for a boolean constant"""
        v = "true" if value else "false"
        n = Node("const", -1, -1, [Node(f"{v}", -1, -1, [])])
        n.data_type = DataType(BaseType.BOOL)
        return n

    @staticmethod
    def create_const_int(value: int) -> Node:
        """creates a node for an integral constant"""
        n = Node("const", -1, -1, [Node(f"{value}", -1, -1, [])])
        n.data_type = DataType(BaseType.INT)
        return n

    @staticmethod
    def compare(u: Node, v: Node) -> bool:
        """deeply compares two nodes w.r.t identifiers"""
        if u.ident != v.ident:  # TODO: numerical compare for real
            return False
        if len(u.children) != len(v.children):
            return False
        n = len(u.children)
        for i in range(0, n):
            if Node.compare(u.children[i], v.children[i]) is False:
                return False
        return True

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
        return None

    def get_children(self, ident: str) -> List[Node]:
        """gets a child node"""
        res: List[Node] = []
        for child in self.children:
            if child.ident == ident:
                res.append(child)
        return res

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

    def const_str(self) -> str:
        """formats nodes of type 'const'"""
        # TODO: missing pointers, ...
        if self.ident != "const":
            return str(self)
        match self.data_type.base:
            case BaseType.BOOL | BaseType.INT:
                return self.children[0].ident
        print(f"Node.const_str(..) is unimplemented for type'{self.data_type.base}'")
