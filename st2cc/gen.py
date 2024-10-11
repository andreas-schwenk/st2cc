"""
gen.py

Description:
    Generation of C code.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from st2cc.ast import Node


class CodeGenerator:
    """C Code generation"""

    def __init__(self, ast: Node) -> None:
        self.ast: Node = ast

    def run(self) -> None:
        """start code generation"""
        pass
