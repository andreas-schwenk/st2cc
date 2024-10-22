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
from st2cc.sym import Sym
from st2cc.pah import parse_address


class SemanticAnalysis:
    """
    Semantic analysis implementation: This phase checks data types,
    creates symbol tables, and determines the data types for each node in the
    abstract syntax tree (AST). The output is a modified AST with type
    annotations. The implementation follows a term rewriting system (TRS)
    approach. The rules are defined within the methods in the form U -> V,
    where U represents the pattern to be matched, and V represents the
    substitution. Type annotations are denoted by “:”. For example, expr:bool
    assigns the type bool to the expression expr. Queries applied to the symbol
    table of a node are indicated by “#”.
    """

    def __init__(self, ast: Node):
        self.ast: Node = ast

    def run(self) -> None:
        """run semantic analysis"""
        self.__run_recursively(self.ast)

    def __run_recursively(self, node: Node) -> Node:
        """
        Runs the analysis for given node.
        """
        data_type: Node = None
        match node.ident:
            case "file":
                self.__file(node)
            case "program":
                self.__program(node)
            case "statements":
                self.__statements(node)
            case "if":
                self.__if(node)
            case "variable":
                data_type = self.__variable(node)
            case "assign" | "mul" | "or" | "and" | "add" | "sub":
                data_type = self.__bin_op(node)
            case "call":
                data_type = self.__call(node)
            case "bool" | "int":
                data_type = self.__const(node)
            case _:
                self.__error(
                    node, f"SemanticAnalysis: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                return None
        return data_type

    def __file(self, node: Node) -> None:
        """semantical analysis for file-node"""
        if len(node.get_children("program")) != 1:
            self.__error(node, "exactly one 'PROGRAM' must be implemented")
        for s in node.children:
            self.__run_recursively(s)

    def __program(self, node: Node) -> None:
        """
        "program"(ID,variables,statements)
            -> "program"(ID,statements) # symbols <- variables;
        """
        # build symbols from variables subtree
        if node.children[1] is not None:
            for v in node.children[1].children:
                ident = v.children[0].ident
                data_type = v.children[1].clone()
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
        """
        "if"(expr,a,b) -> "if"(expr:bool,a,b);
        """
        cond = node.children[0]
        cond_data_type = self.__run_recursively(cond)
        if not Node.compare(cond_data_type, Node("bool")):
            self.__error(cond, "if statement condition must be boolean")
        cond.data_type = cond_data_type
        statements_if = node.children[1]
        for s in statements_if.children:
            self.__run_recursively(s)
        statements_else = node.children[2]
        for s in statements_else.children:
            self.__run_recursively(s)

    def __variable(self, node: Node) -> Node:
        """semantical analysis for var-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident)
        if sym is None:
            self.__error(node, f"unknown symbol '{ident}'")
        node.data_type = sym.data_type
        return sym.data_type

    def __bin_op(self, node: Node) -> Node:
        """
        op(u,v) -> op(u,v):type(u), with type(u)==type(v)
        """
        lhs = node.children[0]
        lhs_data_type = self.__run_recursively(lhs)
        rhs = node.children[1]
        rhs_data_type = self.__run_recursively(rhs)
        if Node.compare(lhs.data_type, rhs.data_type) is False:
            self.__error(
                node,
                f"incompatible types for '{node.ident}':"
                + f" left-hand side '{lhs_data_type}',"
                + f" right-hand side '{rhs_data_type}'",
            )
        node.data_type = lhs_data_type
        return lhs_data_type

    def __call(self, node: Node) -> Node:
        """
        ID(...params) -> ID(...params):type(<function(ID)>);
        """

        # get function

        return TODO

    def __const(self, node: Node) -> Node:
        """
        "bool"(value) -> "const"(value):bool;
        "int"(value) -> "const"(value):int;
        ...
        """
        node.data_type = Node(node.ident)
        node.ident = "const"
        return node.data_type

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
