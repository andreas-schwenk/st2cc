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

from st2cc.ast import Node
from st2cc.lex import Lexer, TokenType


class Parser:
    """Parser"""

    def __init__(self, lex: Lexer) -> None:
        self.lex: Lexer = lex
        self.lex.next()

    def parse(self) -> Node:
        """parses the ST file"""
        root = self.__program()
        root.set_parent()
        return root

    def __program(self) -> Node:
        """
        program = "PROGRAM" ID "VAR" variable* "END_VAR" statement* "END_PROGRAM";
        """
        node = self.lex.expect(TokenType.KEYWORD, "program")
        ident = self.lex.expect(TokenType.IDENT)
        variables = self.lex.expect(TokenType.KEYWORD, "var")
        while not self.lex.peek(TokenType.KEYWORD, "end_var"):
            variables.children.append(self.__variable())
        self.lex.expect(TokenType.KEYWORD, "end_var")
        statements = self.lex.node("statements")
        while not self.lex.peek(TokenType.KEYWORD, "end_program"):
            statements.children.append(self.__statement())
        node.children = [
            ident,
            variables,
            statements,
        ]
        return node

    def __variable(self) -> Node:
        """
        variable = ID [ "AT" ADDR ] ":" type ";"
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
        type = "BOOL" | "INT" | "REAL";
        """
        node = self.lex.node("base")
        b = self.lex.expect(TokenType.KEYWORD)
        node.children = [b]
        if b.ident not in ["bool", "int", "real"]:
            self.lex.error("unknown type 't'")
        return node

    def __statement(self) -> Node:
        """
        statement = if | assignment;
        """
        match self.lex.token.ident:
            case "if":
                return self.__if()
            case _:
                return self.__assignment()

    def __if(self) -> Node:
        """
        if = "IF" expr "THEN" statement* [ "ELSE" statement* "END_IF" ];
        """
        node = self.lex.node("if")
        self.lex.expect(TokenType.KEYWORD, "if")
        condition = self.__expression()
        self.lex.expect(TokenType.KEYWORD, "then")
        statements_if = self.lex.node("statements")
        while not self.lex.peek(TokenType.KEYWORD, "else") and not self.lex.peek(
            TokenType.KEYWORD, "end_if"
        ):
            statements_if.children.append(self.__statement())
        statements_else = self.lex.node("statements")
        if self.lex.peek(TokenType.KEYWORD, "else"):
            self.lex.next()
            while not self.lex.peek(TokenType.KEYWORD, "end_if"):
                statements_else.children.append(self.__statement())
        self.lex.expect(TokenType.KEYWORD, "end_if")
        node.children = [condition, statements_if, statements_else]
        return node

    def __assignment(self) -> Node:
        """
        assignment = ID ":=" expr ";";
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
        expr = or;
        """
        return self.__or()

    def __or(self) -> Node:
        """
        or = and { "OR" and };
        """
        node = self.__and()
        while self.lex.peek(TokenType.KEYWORD, "or"):
            self.lex.next()
            node = self.lex.node("or", [node, self.__and()])
        return node

    def __and(self) -> Node:
        """
        and = mul { "AND" mul };
        """
        node = self.__mul()
        while self.lex.peek(TokenType.KEYWORD, "and"):
            self.lex.next()
            node = self.lex.node("and", [node, self.__mul()])
        return node

    def __mul(self) -> Node:
        """
        mul = unary { "*" unary };
        """
        node = self.__unary()
        while self.lex.peek(TokenType.DELIMITER, "*"):
            self.lex.next()
            node = self.lex.node("mul", [node, self.__unary()])
        return node

    def __unary(self) -> Node:
        """
        unary = "TRUE" | "FALSE" | REAL | INT | "(" expr ")";
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
            res = self.lex.node("var", [self.lex.node(tk)])
        elif self.lex.peek(TokenType.DELIMITER, "("):
            self.lex.next()
            expr = self.__expression()
            self.lex.expect(TokenType.DELIMITER, ")")
            res = expr
        else:
            self.lex.error("expected unary expression")
        return res
