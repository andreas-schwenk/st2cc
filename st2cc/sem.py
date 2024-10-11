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
from st2cc.sym import BaseType, DataType, Sym, Address


class SemanticAnalysis:
    """
    Semantic analysis implementation. Checks data types, creates the symbol tables
    and determines the data types for each node. The result is an altered AST.

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
                    addr = v.children[2]
                    if addr is not None:
                        sym.address = Address()
                        sym.address.parse(addr.children[0].ident[1:])
                    node.symbols[ident] = sym
                # remove var subtree
                del node.children[1]
                # process statements
                self.__run_recursively(node.children[1])
                return None

            case "statements":
                for s in node.children:
                    self.__run_recursively(s)
                return None

            case "if":
                cond = node.children[0]
                cond_dtype = self.__run_recursively(cond)
                if cond_dtype.base != BaseType.BOOL:
                    self.__error(cond, "if statement condition must be boolean")
                cond.dtype = cond_dtype
                statements_if = node.children[1]
                for s in statements_if.children:
                    self.__run_recursively(s)
                statements_else = node.children[2]
                for s in statements_else.children:
                    self.__run_recursively(s)
                return None

            case "var":
                ident = node.children[0].ident
                sym = node.get_symbol(ident)
                if sym is None:
                    self.__error(node, f"unknown symbol '{ident}'")
                return sym.data_type

            case "assign" | "mul":
                lhs = node.children[0]
                lhs_dtype = self.__run_recursively(lhs)
                rhs = node.children[1]
                rhs_dtype = self.__run_recursively(rhs)
                if (
                    lhs_dtype.base != rhs_dtype.base
                ):  # TODO: check entire type, including pointer, ...
                    self.__error(
                        node,
                        f"incompatible types for '{node.ident}':"
                        + f" left-hand side '{lhs_dtype}',"
                        + f" right-hand side '{rhs_dtype}'",
                    )
                node.dtype = lhs_dtype
                return lhs_dtype

            case "bool":
                node.dtype = DataType(BaseType.BOOL)
                return node.dtype

            case "int":
                node.dtype = DataType(BaseType.INT)
                return node.dtype

            case _:
                self.__error(
                    node, f"SemanticAnalysis: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                return None

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(0)
