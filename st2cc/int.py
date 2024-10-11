"""
int.py

Description:
    ST intermediate code interpreter

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

import sys

from st2cc.ast import Node


class Interpreter:
    """ST intermediate code interpretation"""

    def __init__(self, program: Node) -> None:
        self.program: Node = program

    def run(self) -> None:
        """start code interpretation"""
        self.run_rec(self.program)

    def run_rec(self, node: Node) -> Node:
        """interpret node recursively"""
        match node.ident:
            case "program":
                return None
            case _:
                self.__error(
                    node, f"Interpretation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                return None

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(0)
