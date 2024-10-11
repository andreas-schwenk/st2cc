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
import csv
from typing import Dict, List

from st2cc.ast import Node


class TestData:

    def __init__(self) -> None:
        self.data: Dict[str,List[int]] = {}

    def read(self, csv_file_path) -> None:
        with open(csv_file_path, mode="r", encoding="utf-8") as f:
            r = csv.reader(f)
            for row in r:
                if row and not row[0].startswith("#"):
                    self.data[row[0]] = list(map(int, row[1:]))  # TODO: error handling


class Interpreter:
    """ST intermediate code interpretation"""

    def __init__(self, program: Node, test_data: TestData) -> None:
        self.program: Node = program
        self.test_data: TestData = test_data

    def run(self) -> None:
        """start code interpretation"""
        self.run_rec(self.program)

    def run_rec(self, node: Node) -> Node:
        """interpret node recursively"""
        match node.ident:
            case "program":
                self.set_symbol_values(node)
                return None
            case _:
                self.__error(
                    node, f"Interpretation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                return None

    def set_symbol_values(self, node: Node) -> None:
        """sets the I/O test values to the currents node symbols"""
        for sym in node.symbols.values():
            if sym.address is None:
                continue
            addr_str = str(sym.address) TODO: leave out value
            if addr_str in self.test_data.data:
                sym.address.value = self.test_data[str(sym.address)]
                bp = 1337


    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(0)
