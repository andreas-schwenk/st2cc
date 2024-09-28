"""
sem.py

Description:
    Performs semantic analysis on the abstract syntax tree (AST), constructing 
    the symbol table and determining the data type for each node. 
    Modifies the AST as necessary to reflect semantic information.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

import sys

from st2cc.ast import Node
from st2cc.sym import BaseType, DataType, Sym


class SemanticAnalysis:
    """
    Semantic analysis implementation.

    Attributes:
        ast (Node): The abstract syntax tree.

    Methods:
        run()
            Runs the semantic analysis on the given abstract syntax tree.
    """

    def __init__(self, ast: Node):
        self.ast: Node = ast

    def run(self) -> None:
        """run semantic analysis"""
        self.__run_recursively(self.ast)

    def __run_recursively(self, node: Node) -> DataType:
        """
        Runs the analysis for given node.
        """
        match node.ident:

            case "program":
                # build symbols from "var" subtree
                for v in node.children[1].children:
                    ident = v.children[0].ident
                    data_type = DataType(
                        BaseType[v.children[1].children[0].ident.upper()]
                    )
                    sym = Sym(ident, data_type)
                    node.symbols[ident] = sym
                # remove var subtree
                del node.children[1]
                # process statements
                self.__run_recursively(node.children[1])
                return None

            case "statements":
                for c in node.children:
                    self.__run_recursively(c)
                return None

            case "if":
                # TODO
                return None

            case _:
                self.__error(node, f"SemanticAnalysis: UNIMPLEMENTED '{node.ident}'")

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(0)
