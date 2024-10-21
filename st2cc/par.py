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
        return part

    def __program(self) -> Node:
        """
        program = "program" ID [variables] statements "end_program"
            -> "program"(ID, [variables], statements);
        """
        node = self.lex.expect(TokenType.KEYWORD, "program")
        ident = self.lex.expect(TokenType.IDENT)
        variables = None
        if self.lex.peek(TokenType.KEYWORD, "var"):
            variables = self.__variables()
        statements = self.__statements(["end_program"])
        node.children = [
            ident,
            variables,
            statements,
        ]
        return node

    def __function(self) -> Node:
        """
        function = "function" ID [variables] statements "end_function"
            -> "function"(ID, [variables], statements)
        """
        TODO

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

    def __variables(self) -> Node:
        """
        variables = "VAR" {variable} "END_VAR"
            -> "variables"(...variable);
        """
        variables = self.lex.expect(TokenType.KEYWORD, "var")
        variables.ident = "variables"
        while not self.lex.is_end() and not self.lex.peek(TokenType.KEYWORD, "end_var"):
            variables.children.append(self.__variable())
        self.lex.expect(TokenType.KEYWORD, "end_var")
        return variables

    def __variable(self) -> Node:
        """
        variable = ID [ "AT" ADDR ] ":" type ";"
            -> "variable"(ID, type, ["addr"(ADDR)]);
        """
        node = self.lex.node("variable")
        ident = self.lex.expect(TokenType.IDENT)
        addr = self.lex.node("addr")
        if self.lex.peek(TokenType.KEYWORD, "at"):
            self.lex.next()
            addr.children.append(self.lex.expect(TokenType.ADDR))
        self.lex.expect(TokenType.DELIMITER, ":")
        t = self.__type()
        self.lex.expect(TokenType.DELIMITER, ";")
        node.children = [ident, t, addr]
        return node

    def __type(self) -> Node:
        """
        type = "BOOL" -> "base"("bool")
            | "INT" -> "base"("int")
            | "REAL" -> "base"("real");
        """
        node = self.lex.node("base")
        b = self.lex.expect(TokenType.KEYWORD)
        node.children = [b]
        if b.ident not in ["bool", "int", "real"]:
            self.lex.error("unknown type 't'")
        return node

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
        statements_else: Node = None
        if self.lex.peek(TokenType.KEYWORD, "else"):
            self.lex.next()
            statements_else = self.__statements(["elseif", "else", "end_if"])
        self.lex.expect(TokenType.KEYWORD, "end_if")
        node.children = [condition, statements_if, statements_else]
        return node

    def __assignment(self) -> Node:
        """
        assignment = ID ":=" expr ";"
            -> "assign"("var"(ID), expr);
        """
        node = self.lex.node("assign")
        lhs = self.lex.node("var", [self.lex.expect(TokenType.IDENT)])
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
        and = mul { "AND" mul }
            -> mul | "and"(and, mul);
        """
        node = self.__mul()
        while self.lex.peek(TokenType.KEYWORD, "and"):
            self.lex.next()
            node = self.lex.node("and", [node, self.__mul()])
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
            | ID -> "var"(ID)
            | ID "(" expr@args { "," expr@args } ")" -> "call"(...args)
            | "(" expr ")" -> expr;
        """
        res: Node = None
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
                args: List[Node] = []
                args.append(self.__expression())
                while self.lex.peek(TokenType.DELIMITER, ","):
                    self.lex.next()
                    args.append(self.__expression())
                self.lex.expect(TokenType.DELIMITER, ")")
                res = self.lex.node("call", args)
            else:
                res = self.lex.node("var", [self.lex.node(tk)])
        elif self.lex.peek(TokenType.DELIMITER, "("):
            self.lex.next()
            expr = self.__expression()
            self.lex.expect(TokenType.DELIMITER, ")")
            res = expr
        else:
            self.lex.error("expected unary expression")
        return res
