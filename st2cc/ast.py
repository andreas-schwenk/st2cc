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

from st2cc.sym import Symbol


NIL = "nil"


class Node:
    """abstract syntax tree node"""

    def __init__(
        self, ident: str, children: List[Node] = None, row: int = -1, col: int = -1
    ) -> None:
        self.ident: str = ident
        self.row: int = row
        self.col: int = col
        self.data_type: Node = None if ident == NIL else Node(NIL)
        self.symbols: Dict[str, Symbol] = {}
        self.parent: Node = None
        self.children: List[Node] = children if children is not None else []

    def clone(self) -> Node:
        """clones a node"""
        c = Node(self.ident)
        c.row = self.row
        c.col = self.col
        c.data_type = (
            None if self.data_type is None else self.data_type.clone()
        )  # TODO: OK for complex types??
        c.symbols = self.symbols
        c.parent = self.parent
        for child in self.children:
            c.children.append(child.clone())
        return c

    def is_nil(self) -> bool:
        """checks, if the node is NIL"""
        return self.ident == NIL

    @staticmethod
    def create_nil() -> Node:
        """creates a node for nil - not in list"""
        return Node(NIL)

    @staticmethod
    def create_const_bool(value: bool) -> Node:
        """creates a node for a boolean constant"""
        v = "true" if value else "false"
        n = Node("const", [Node(v)])
        n.data_type = Node("bool")
        return n

    @staticmethod
    def create_const_int(value: int) -> Node:
        """creates a node for an integral constant"""
        n = Node("const", [Node(f"{value}")])
        n.data_type = Node("int")
        return n

    @staticmethod
    def compare(u: Node, v: Node) -> bool:
        """deeply compares two nodes w.r.t identifiers"""
        if u.ident != v.ident:  # TODO: numerical compare for real
            return False
        n = len(u.children)
        if n != len(v.children):
            return False
        for i in range(0, n):
            if Node.compare(u.children[i], v.children[i]) is False:
                return False
        return True

    def set_parent(self) -> None:
        """sets parent recursively"""
        for c in self.children:
            c.parent = self
            c.set_parent()

    def get_symbol(self, ident: str, scopes: List[str] = None) -> Symbol:
        """get symbol from most inner matching scope"""
        n = self
        while n is not None:
            if ident in n.symbols:
                sym = n.symbols[ident]
                if scopes is None or sym.scope in scopes:
                    return sym
            n = n.parent
        return None

    def get_symbols(self, scope="") -> List[Symbol]:
        """counts the number of symbols by scope"""
        res: List[Symbol] = []
        n = self
        while n is not None:
            for sym in n.symbols.values():
                if sym.scope == scope:
                    res.append(sym)
            n = n.parent
        return res

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
        t = "" if self.data_type is None else self.data_type.brackets_str()
        s = ""
        if show_position:
            s += f"{self.row}:{self.col}:"
        s += f"{self.ident}:<{t}>\n"
        for sym in self.symbols.values():
            # s += ("  " * (indentation + 1)) + f"SYMBOL: {sym}\n"
            s += self.indentation(f"SYMBOL: {sym}\n", indentation + 1)
        for ci in self.children:
            s += "  " * (indentation + 1)
            s += ci.custom_str(show_position, indentation + 1)
        return s

    def brackets_str(self) -> str:
        """stringify to brackets"""
        s = self.ident
        n = len(self.children)
        if n > 0:
            s += "("
            for i in range(0, n):
                if i > 0:
                    s += ","
                s += self.children[i].brackets_str()
            s += ")"
        return s

    def indentation(self, code: str, cnt: int = 1) -> str:
        """indents code by 4 spaces"""
        ws = "  " * cnt
        return "\n".join(map(lambda line: ws + line, code.splitlines())) + "\n"
