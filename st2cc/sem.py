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
        self.__run(self.ast)

    def __run(self, node: Node) -> Node:
        """
        Runs the analysis for given node.
        """
        data_type: Node = None
        match node.ident:
            case "file":
                self.__file(node)
            case "program" | "function":
                self.__program_function(node)
            case "statements":
                self.__statements(node)
            case "if":
                self.__if(node)
            case "variable":
                data_type = self.__variable(node)
            case "geq" | "lt" | "gt" | "leq":
                data_type = self.__cmp(node)
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
        """
        semantical analysis for file-node
        TODO-doc: brings everything to the root symbol table
        """
        for child in node.children:
            scope = child.ident
            ident = child.children[0].ident
            data_type = Node("void") if child.ident == "program" else child.children[1]
            # TODO: method self.add_sym(..) that checks for duplicates
            sym = Sym(scope, ident, data_type)
            sym.code = child
            node.symbols[ident] = sym
        node.children = []
        for sym in node.symbols.values():
            if sym.code is not None:
                self.__run(sym.code)
        # check if there is a program
        if len(node.get_symbols("program")) != 1:
            self.__error(node, "exactly one 'PROGRAM' must be implemented")

    def __program_function(self, node: Node) -> None:
        """
        "program"(ID,variable_blocks,statements)
            -> "program"(ID,statements) # symbols <- variable_blocks;
        "function"(ID,data_type,variable_blocks,statements)
            -> "function"(ID,data_type,statements) # symbols <- variable_blocks;
        """
        # TODO: check that ADDR is only at allowed places
        is_program = node.ident == "program"
        ident = node.children[0].ident
        return_type: Node = None if is_program else node.children[1]
        variable_blocks: Node = node.children[1 if is_program else 2]
        statements: Node = node.children[2 if is_program else 3]
        # for functions: declare a local variable with the same name as the
        # function, which will store the return value.
        if not is_program:
            node.symbols[ident] = Sym("local", ident, return_type)
        # build symbols from variables subtree
        # TODO: check, if symbol already exists in same scope via self.add_symbol(..)
        for block in variable_blocks.children:
            scope = ""
            if block.ident == "variables":
                scope = "local"
            elif block.ident == "input_variables":
                scope = "parameter"
            else:
                self.__error(block, f"unimplemented variable block '{block.ident}'")
            for variable in block.children:
                ident = variable.children[0].ident
                data_type = variable.children[1].clone()
                sym = Sym(scope, ident, data_type)
                addr = variable.children[2]
                if addr is not None:
                    sym.address = parse_address(addr.children[0].ident[1:])
                node.symbols[ident] = sym
        # remove var subtree
        del node.children[1 if is_program else 2]
        # process statements
        self.__run(statements)

    def __statements(self, node: Node) -> None:
        """semantical analysis for statements-node"""
        for s in node.children:
            self.__run(s)

    def __if(self, node: Node) -> None:
        """
        "if"(expr,a,b) -> "if"(expr:bool,a,b);
        """
        cond = node.children[0]
        cond_data_type = self.__run(cond)
        if not Node.compare(cond_data_type, Node("bool")):
            self.__error(cond, "if statement condition must be boolean")
        cond.data_type = cond_data_type
        statements_if = node.children[1]
        for s in statements_if.children:
            self.__run(s)
        statements_else = node.children[2]
        for s in statements_else.children:
            self.__run(s)

    def __variable(self, node: Node) -> Node:
        """semantical analysis for var-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident, ["parameter", "local"])
        if sym is None:
            self.__error(node, f"unknown symbol '{ident}'")
        node.data_type = sym.data_type
        return sym.data_type

    def __cmp(self, node: Node) -> Node:
        """
        op(u,v) -> op(u,v):type(u), with type(u)==type(v)
        """
        # TODO: check in detail, which types can be compared
        op = node.ident
        lhs_type = self.__run(node.children[0])
        rhs_type = self.__run(node.children[1])
        if Node.compare(lhs_type, rhs_type) is False:
            self.__error(
                node,
                f"incompatible types for '{op}':"
                + f" left-hand side '{lhs_type}',"
                + f" right-hand side '{rhs_type}'",
            )
        res = Node("bool")
        node.data_type = res
        return res

    def __bin_op(self, node: Node) -> Node:
        """
        op(u,v) -> op(u,v):type(u), with type(u)==type(v)
        """
        op = node.ident
        lhs_type = self.__run(node.children[0])
        rhs_type = self.__run(node.children[1])
        if Node.compare(lhs_type, rhs_type) is False:
            self.__error(
                node,
                f"incompatible types for '{op}':"
                + f" left-hand side '{lhs_type}',"
                + f" right-hand side '{rhs_type}'",
            )
        node.data_type = lhs_type
        return lhs_type

    def __call(self, node: Node) -> Node:
        """
        ID(...params) -> ID(...params):type(<function(ID)>);
        """
        ident = node.children[0].ident
        sym = node.get_symbol(ident, "function")
        if sym is None:
            self.__error(node, f"unknown function '{ident}'")
        # TODO: must check, if params and args match
        return sym.data_type

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
