"""
par.py

Description:
    Parser for the ST grammar. Implemented as top-down parser with a lookahead
    of 1, i.e. LL(1).

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from typing import List

from st2cc.ast import Node
from st2cc.lex import Lexer, TokenType


class Parser:
    """
    This class implements a Structured Text (ST) parser. Each parsing method is
    prefixed with __ and corresponds to a specific parsing rule. Every rule is
    defined in the form r = G -> E;

    G represents the formal grammar, specified in Extended Backus-Naur Form
    (EBNF):
    - ID, INT, REAL, ADDR and quoted strings (e.g. >>"VAR"<<) are terminal tokens
    - Identifiers (e.g. >>expr<<) are non-terminals, which refer to another rule
    - { }  denotes a repetition (zero or more occurrences)
    - [ ]  denotes a optionality (zero or one occurrence)
    - @    defines an alternative name for a non-terminal

    E = r(X, Y, ...) | U  is a generated expression. Generated expressions
    collectively form the synthesized Abstract Syntax Tree (AST).
    - r is a constant identifier
    - X, Y, ... are the arguments (recursively defined subnodes).
    - U is a unary expression
    Unary expressions have one of the following forms:
    - Identifiers refer to another generated expression
    - [ ]  denotes optionality. The implementation uses >>None<< for zero occurrences
    - quotes strings (e.g. >>"bool"<<) are terminal values
    - ... is the rest-operator, which splits the repetition from grammar into
      a list of arguments.
    """

    def __init__(self, lex: Lexer) -> None:
        self.lex: Lexer = lex
        self.lex.next()

    def parse(self) -> Node:
        """parses the ST file"""
        root = self.__file()
        root.set_parent()
        return root

    def __file(self) -> Node:
        """
        file = {part}
            -> "file"(...part);
        """
        node = self.lex.node("file")
        while not self.lex.is_end():
            part = self.__part()
            node.children.append(part)
        return node

    def __part(self) -> Node:
        """
        part = program -> program
            | function -> function;
        """
        part: Node = None
        if self.lex.peek(TokenType.KEYWORD, "program"):
            part = self.__program()
        elif self.lex.peek(TokenType.KEYWORD, "function"):
            part = self.__function()
        else:
            self.lex.error("expected 'PROGRAM' or 'FUNCTION'")
        return part

    def __program(self) -> Node:
        """
        program = "program" ID variables_blocks statements "end_program"
            -> "program"(ID, variables_blocks, statements);
        """
        program = self.lex.expect(TokenType.KEYWORD, "program")
        ident = self.lex.expect(TokenType.IDENT)
        variable_blocks = self.__variable_blocks()
        statements = self.__statements(["end_program"])
        self.lex.expect(TokenType.KEYWORD, "end_program")
        program.children = [
            ident,
            variable_blocks,
            statements,
        ]
        return program

    def __function(self) -> Node:
        """
        function = "function" ID ":" type variables_blocks statements "end_function"
            -> "function"(ID, type, variables_blocks, statements)
        """
        function = self.lex.expect(TokenType.KEYWORD, "function")
        ident = self.lex.expect(TokenType.IDENT)
        self.lex.expect(TokenType.DELIMITER, ":")
        return_type = self.__type()
        variables_blocks = self.__variable_blocks()
        statements = self.__statements(["end_function"])
        self.lex.expect(TokenType.KEYWORD, "end_function")
        function.children = [
            ident,
            return_type,
            variables_blocks,
            statements,
        ]
        return function

    def __variable_blocks(self) -> Node:
        """
        variable_blocks = {variable_block}
            -> "variable_blocks"(...variable_block);
        """
        blocks = self.lex.node("variable_blocks")
        while self.lex.peek(TokenType.KEYWORD, "var") or self.lex.peek(
            TokenType.KEYWORD, "var_input"
        ):
            blocks.children.append(self.__variable_block())
        return blocks

    def __variable_block(self) -> Node:
        """
        variable_block = "VAR" {variable(False)} "END_VAR" -> "variables"(...variable)
            | "VAR_INPUT" {variable(True)} "END_VAR" -> "input_variables"(...variable);
        """
        block = Node.create_nil()
        if self.lex.peek(TokenType.KEYWORD, "var"):
            block = self.lex.expect(TokenType.KEYWORD, "var")
            block.ident = "variables"
        elif self.lex.peek(TokenType.KEYWORD, "var_input"):
            block = self.lex.expect(TokenType.KEYWORD, "var_input")
            block.ident = "input_variables"
        else:
            self.lex.error("expected 'var' or 'var_input'")
        while not self.lex.is_end() and not self.lex.peek(TokenType.KEYWORD, "end_var"):
            block.children.append(self.__variable())
        self.lex.expect(TokenType.KEYWORD, "end_var")
        return block

    def __variable(self) -> Node:
        """
        variable = ID [ "AT" ADDR ] ":" type ";"
            ->  "variable"(ID, type, ["addr"(ADDR)]);
        """
        node = self.lex.node("variable")
        ident = self.lex.expect(TokenType.IDENT)
        addr = Node.create_nil()
        if self.lex.peek(TokenType.KEYWORD, "at"):
            addr = self.lex.node("addr")
            self.lex.next()
            addr.children.append(self.lex.expect(TokenType.ADDR))
        self.lex.expect(TokenType.DELIMITER, ":")
        t = self.__type()
        self.lex.expect(TokenType.DELIMITER, ";")
        node.children = [ident, t, addr]
        return node

    def __statements(self, stop_keywords: List[str]) -> Node:
        """
        statements = {statement}
            -> "statements"(...statement);
        """
        statements = self.lex.node("statements")
        while not self.lex.is_end():
            if self.lex.peek_list(TokenType.KEYWORD, stop_keywords):
                break
            statements.children.append(self.__statement())
        return statements

    def __type(self) -> Node:
        """
        type = "BOOL" -> "bool"
            | "INT" -> "int"
            | "REAL" -> "real";
        """
        base = self.lex.expect(TokenType.KEYWORD)
        if base.ident not in ["bool", "int", "real"]:
            self.lex.error("unknown type 't'")
        return base

    def __statement(self) -> Node:
        """
        statement = if -> if | assignment -> assignment;
        """
        match self.lex.token.ident:
            case "if":
                return self.__if()
            case _:
                return self.__assignment()

    def __if(self) -> Node:
        """
        if = "IF" expr "THEN" statements@a [ "ELSE" statements@b "END_IF" ]
            -> "if"(expr, a, [b]);
        """
        node = self.lex.node("if")
        self.lex.expect(TokenType.KEYWORD, "if")
        condition = self.__expression()
        self.lex.expect(TokenType.KEYWORD, "then")
        statements_if = self.__statements(["elseif", "else", "end_if"])
        statements_else: Node = Node.create_nil()
        if self.lex.peek(TokenType.KEYWORD, "else"):
            self.lex.next()
            statements_else = self.__statements(["elseif", "else", "end_if"])
        self.lex.expect(TokenType.KEYWORD, "end_if")
        node.children = [condition, statements_if, statements_else]
        return node

    def __assignment(self) -> Node:
        """
        assignment = ID ":=" expr ";"
            -> "assign"("variable"(ID), expr);
        """
        node = self.lex.node("assign")
        lhs = self.lex.node("variable", [self.lex.expect(TokenType.IDENT)])
        self.lex.expect(TokenType.DELIMITER, ":=")
        rhs = self.__expression()
        self.lex.expect(TokenType.DELIMITER, ";")
        node.children = [lhs, rhs]
        return node

    def __expression(self) -> Node:
        """
        expr = or
            -> or;
        """
        return self.__or()

    def __or(self) -> Node:
        """
        or = and { "OR" and }
            -> and | "or"(or, and);
        """
        node = self.__and()
        while self.lex.peek(TokenType.KEYWORD, "or"):
            self.lex.next()
            node = self.lex.node("or", [node, self.__and()])
        return node

    def __and(self) -> Node:
        """
        and = cmp { "AND" cmp }
            -> cmp | "and"(and, cmp);
        """
        node = self.__cmp()
        while self.lex.peek(TokenType.KEYWORD, "and"):
            self.lex.next()
            node = self.lex.node("and", [node, self.__cmp()])
        return node

    def __cmp(self) -> Node:
        """
        cmp = add [ ">" add ] -> add | "gt"(cmp, add)
            | add [ "<" add ] -> add | "lt"(cmp, add)
            | add [ ">=" add ] -> add | "geq"(cmp, add)
            | add [ "<=" add ] -> add | "leq"(cmp, add);
        """
        node = self.__add()
        if self.lex.peek(TokenType.DELIMITER, ">"):
            self.lex.next()
            node = self.lex.node("gt", [node, self.__add()])
        elif self.lex.peek(TokenType.DELIMITER, "<"):
            self.lex.next()
            node = self.lex.node("lt", [node, self.__add()])
        elif self.lex.peek(TokenType.DELIMITER, ">="):
            self.lex.next()
            node = self.lex.node("geq", [node, self.__add()])
        elif self.lex.peek(TokenType.DELIMITER, "<="):
            self.lex.next()
            node = self.lex.node("leq", [node, self.__add()])
        return node

    def __add(self) -> Node:
        """
        add = mul { ("+"|"-") mul }
            -> mul | "add|sub"(add, unary);
        """
        node = self.__mul()
        while self.lex.peek(TokenType.DELIMITER, "+") or self.lex.peek(
            TokenType.DELIMITER, "-"
        ):
            is_add = self.lex.peek(TokenType.DELIMITER, "+")
            self.lex.next()
            node = self.lex.node("add" if is_add else "sub", [node, self.__mul()])
        return node

    def __mul(self) -> Node:
        """
        mul = unary { "*" unary }
            -> unary | "mul"(mul, unary);
        """
        node = self.__unary()
        while self.lex.peek(TokenType.DELIMITER, "*"):
            self.lex.next()
            node = self.lex.node("mul", [node, self.__unary()])
        return node

    def __unary(self) -> Node:
        """
        unary = "TRUE" -> "bool"("true")
            | "FALSE" -> "bool"("false")
            | REAL -> "real"(real)
            | INT -> "int"(int)
            | ID -> "variable"(ID)
            | ID "(" expr@args { "," expr@arg } ")" -> "call"(ID, args(...arg))
            | "(" expr ")" -> expr;
        """
        res: Node = Node.create_nil()
        if self.lex.peek(TokenType.KEYWORD, "true"):
            self.lex.next()
            res = self.lex.node("bool", [self.lex.node("true")])
        elif self.lex.peek(TokenType.KEYWORD, "false"):
            self.lex.next()
            res = self.lex.node("bool", [self.lex.node("false")])
        elif self.lex.peek(TokenType.REAL):
            tk = self.lex.token.ident
            self.lex.next()
            res = self.lex.node("real", [self.lex.node(tk)])
        elif self.lex.peek(TokenType.INT):
            tk = self.lex.token.ident
            self.lex.next()
            res = self.lex.node("int", [self.lex.node(tk)])
        elif self.lex.peek(TokenType.IDENT):
            tk = self.lex.token.ident
            self.lex.next()
            if self.lex.peek(TokenType.DELIMITER, "("):
                self.lex.next()
                ident = tk
                args: List[Node] = []
                args.append(self.__expression())
                while self.lex.peek(TokenType.DELIMITER, ","):
                    self.lex.next()
                    args.append(self.__expression())
                self.lex.expect(TokenType.DELIMITER, ")")
                res = self.lex.node(
                    "call", [self.lex.node(ident), self.lex.node("args", args)]
                )
            else:
                res = self.lex.node("variable", [self.lex.node(tk)])
        elif self.lex.peek(TokenType.DELIMITER, "("):
            self.lex.next()
            expr = self.__expression()
            self.lex.expect(TokenType.DELIMITER, ")")
            res = expr
        else:
            self.lex.error("expected unary expression")
        return res
