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
from st2cc.pah import parse_address


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
        res: DataType = None
        match node.ident:
            case "program":
                self.__program(node)
            case "statements":
                self.__statements(node)
            case "if":
                self.__if(node)
            case "var":
                res = self.__var(node)
            case "assign" | "mul" | "or":
                res = self.__bin_op(node)
            case "bool" | "int":
                res = self.__const(node)
            case _:
                self.__error(
                    node, f"SemanticAnalysis: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                return None
        return res

    def __program(self, node: Node) -> None:
        """semantical analysis for program-node"""
        # build symbols from "var" subtree
        for v in node.children[1].children:
            ident = v.children[0].ident
            data_type = DataType(BaseType[v.children[1].children[0].ident.upper()])
            sym = Sym(ident, data_type)
            addr = v.children[2]
            if addr is not None:
                sym.address = parse_address(addr.children[0].ident[1:])
            node.symbols[ident] = sym
        # remove var subtree
        del node.children[1]
        # process statements
        self.__run_recursively(node.children[1])

    def __statements(self, node: Node) -> None:
        """semantical analysis for statements-node"""
        for s in node.children:
            self.__run_recursively(s)

    def __if(self, node: Node) -> None:
        """semantical analysis for if-node"""
        cond = node.children[0]
        cond_data_type = self.__run_recursively(cond)
        if cond_data_type.base != BaseType.BOOL:
            self.__error(cond, "if statement condition must be boolean")
        cond.data_type = cond_data_type
        statements_if = node.children[1]
        for s in statements_if.children:
            self.__run_recursively(s)
        statements_else = node.children[2]
        for s in statements_else.children:
            self.__run_recursively(s)

    def __var(self, node: Node) -> DataType:
        """semantical analysis for var-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident)
        if sym is None:
            self.__error(node, f"unknown symbol '{ident}'")
        node.data_type = sym.data_type
        return sym.data_type

    def __bin_op(self, node: Node) -> DataType:
        """semantical analysis for binary-operation-node"""
        lhs = node.children[0]
        lhs_data_type = self.__run_recursively(lhs)
        rhs = node.children[1]
        rhs_data_type = self.__run_recursively(rhs)
        if DataType.compare(lhs.data_type, rhs.data_type) is False:
            self.__error(
                node,
                f"incompatible types for '{node.ident}':"
                + f" left-hand side '{lhs_data_type}',"
                + f" right-hand side '{rhs_data_type}'",
            )
        node.data_type = lhs_data_type
        return lhs_data_type

    def __const(self, node: Node) -> DataType:
        """semantical analysis for const-node"""
        match node.ident:
            case "bool":
                node.data_type = DataType(BaseType.BOOL)
            case "int":
                node.data_type = DataType(BaseType.INT)
        node.ident = "const"
        return node.data_type

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
