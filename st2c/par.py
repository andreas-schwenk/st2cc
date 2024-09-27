"""
LL(1) parser definition
"""

from st2c.ast import Node
from st2c.tok import TokenType
from st2c.lex import Lexer


class Parser:
    """Parser"""

    def __init__(self, lex: Lexer) -> None:
        self.lex: Lexer = lex
        self.lex.next()

    def parse(self) -> Node:
        """parses the ST file"""
        root = self.p_program()
        root.set_parent()
        return root

    def p_program(self) -> Node:
        """
        program = "PROGRAM" ID "VAR" variable* "END_VAR" statement* "END_PROGRAM";
        """
        node = self.lex.expect(TokenType.KEYWORD, "program")
        ident = self.lex.expect(TokenType.IDENT)
        variables = self.lex.expect(TokenType.KEYWORD, "var")
        while not self.lex.peek(TokenType.KEYWORD, "end_var"):
            variables.children.append(self.p_variable())
        self.lex.expect(TokenType.KEYWORD, "end_var")
        statements = self.lex.node("statements")
        while not self.lex.peek(TokenType.KEYWORD, "end_program"):
            statements.children.append(self.p_statement())
        node.children = [
            ident,
            variables,
            statements,
        ]
        return node

    def p_variable(self) -> Node:
        """
        variable = ID ":" type ";"
        """
        node = self.lex.node("variable")
        ident = self.lex.expect(TokenType.IDENT)
        self.lex.expect(TokenType.DELIMITER, ":")
        t = self.p_type()
        self.lex.expect(TokenType.DELIMITER, ";")
        node.children = [ident, t]
        return node

    def p_type(self) -> Node:
        """
        type = "BOOL" | "INT" | "REAL";
        """
        node = self.lex.node("base")
        b = self.lex.expect(TokenType.KEYWORD)
        node.children = [b]
        if b.ident not in ["bool", "int", "real"]:
            self.lex.error("unknown type 't'")
        return node

    def p_statement(self) -> Node:
        """
        statement = if | assignment;
        """
        match self.lex.token.ident:
            case "if":
                return self.p_if()
            case _:
                return self.p_assignment()

    def p_if(self) -> Node:
        """
        if = "IF" expr "THEN" statement* [ "ELSE" statement* "END_IF" ];
        """
        node = self.lex.node("if")
        self.lex.expect(TokenType.KEYWORD, "if")
        condition = self.p_expr()
        self.lex.expect(TokenType.KEYWORD, "then")
        statements_if = self.lex.node("statements")
        while not self.lex.peek(TokenType.KEYWORD, "else") and not self.lex.peek(
            TokenType.KEYWORD, "end_if"
        ):
            statements_if.children.append(self.p_statement())
        statements_else = self.lex.node("statements")
        if self.lex.peek(TokenType.KEYWORD, "else"):
            self.lex.next()
            while not self.lex.peek(TokenType.KEYWORD, "end_if"):
                statements_else.children.append(self.p_statement())
        self.lex.expect(TokenType.KEYWORD, "end_if")
        node.children = [condition, statements_if, statements_else]
        return node

    def p_assignment(self) -> Node:
        """
        assignment = ID ":=" expr ";";
        """
        node = self.lex.node("assign")
        lhs = self.lex.node("var", [self.lex.expect(TokenType.IDENT)])
        self.lex.expect(TokenType.DELIMITER, ":=")
        rhs = self.p_expr()
        self.lex.expect(TokenType.DELIMITER, ";")
        node.children = [lhs, rhs]
        return node

    def p_expr(self) -> Node:
        """
        expr = mul;
        """
        return self.p_mul()

    def p_mul(self) -> Node:
        """
        mul = unary { "*" unary };
        """
        node = self.p_unary()
        while self.lex.peek(TokenType.DELIMITER, "*"):
            self.lex.next()
            node = self.lex.node("mul", [node, self.p_unary()])
        return node

    def p_unary(self) -> Node:
        """
        unary = "TRUE" | "FALSE" | REAL | INT;
        """
        if self.lex.peek(TokenType.KEYWORD, "true"):
            self.lex.next()
            return self.lex.node("bool", [self.lex.node("true")])
        if self.lex.peek(TokenType.KEYWORD, "false"):
            self.lex.next()
            return self.lex.node("bool", [self.lex.node("false")])
        if self.lex.peek(TokenType.REAL):
            tk = self.lex.token.ident
            self.lex.next()
            return self.lex.node("real", [self.lex.node(tk)])
        if self.lex.peek(TokenType.INT):
            tk = self.lex.token.ident
            self.lex.next()
            return self.lex.node("int", [self.lex.node(tk)])
        if self.lex.peek(TokenType.IDENT):
            tk = self.lex.token.ident
            self.lex.next()
            return self.lex.node("var", [self.lex.node(tk)])
        self.lex.error("expected unary expression")
        return None
