"""
Unit test for class Lexer
"""

import unittest

from st2cc.lex import Lexer, TokenType

SRC = """
PROGRAM Main
    VAR
        x AT %IX0.0: BOOL;
        y AT %QX0.1: BOOL;
    END_VAR
    IF x THEN
        y := TRUE;
    ELSE
        y := FALSE;
    END_IF
END_PROGRAM
"""

EXPECTED = """'program',2,1,TokenType.KEYWORD
'main',2,9,TokenType.IDENT
'var',3,5,TokenType.KEYWORD
'x',4,9,TokenType.IDENT
'at',4,11,TokenType.KEYWORD
'%IX0.0',4,14,TokenType.ADDR
':',4,20,TokenType.DELIMITER
'bool',4,22,TokenType.KEYWORD
';',4,26,TokenType.DELIMITER
'y',5,9,TokenType.IDENT
'at',5,11,TokenType.KEYWORD
'%QX0.1',5,14,TokenType.ADDR
':',5,20,TokenType.DELIMITER
'bool',5,22,TokenType.KEYWORD
';',5,26,TokenType.DELIMITER
'end_var',6,5,TokenType.KEYWORD
'if',7,5,TokenType.KEYWORD
'x',7,8,TokenType.IDENT
'then',7,10,TokenType.KEYWORD
'y',8,9,TokenType.IDENT
':=',8,11,TokenType.DELIMITER
'true',8,14,TokenType.KEYWORD
';',8,18,TokenType.DELIMITER
'else',9,5,TokenType.KEYWORD
'y',10,9,TokenType.IDENT
':=',10,11,TokenType.DELIMITER
'false',10,14,TokenType.KEYWORD
';',10,19,TokenType.DELIMITER
'end_if',11,5,TokenType.KEYWORD
'end_program',12,1,TokenType.KEYWORD"""


class LexerTestClass(unittest.TestCase):
    """Unit tests for the lexer"""

    def test(self):
        """test"""

        expected = EXPECTED.split("\n")
        n = len(expected)
        i = 0

        lexer = Lexer(SRC)
        lexer.next()
        while lexer.token.type != TokenType.END:
            actual = str(lexer.token)
            self.assertGreater(n, i)
            self.assertEqual(expected[i], actual)
            lexer.next()
            i += 1
        self.assertEqual(i, n)


if __name__ == "__main__":
    unittest.main()
