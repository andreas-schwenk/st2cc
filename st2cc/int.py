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
from st2cc.sym import Sym, AddressDirection


class TestData:
    """
    Test data sourced from a CSV file, used to provide values for input addresses.

    Attributes
    ----------
    data : Dict[str, List[int]]
        TODO.
    active_idx : int
        The current sample index.
    sample_count : int
        The number of samples for each address.
    """

    def __init__(self) -> None:
        self.data: Dict[str, List[int]] = {}
        self.active_idx: int = 0
        self.sample_count: int = -1

    def read(self, csv_file_path) -> None:
        """reads an CSV file"""
        with open(csv_file_path, mode="r", encoding="utf-8") as f:
            r = csv.reader(f)
            for row in r:
                if row and not row[0].startswith("#"):
                    self.data[row[0]] = list(map(int, row[1:]))  # TODO: error handling
        for samples in self.data.values():
            if self.sample_count < 0:
                self.sample_count = len(samples)
            elif self.sample_count != len(samples):
                print(f"Error: unbalanced length of samples in file '{csv_file_path}'")
                sys.exit(-1)


class Interpreter:
    """ST intermediate code interpretation"""

    def __init__(self, program: Node, test_data: TestData) -> None:
        self.program: Node = program
        self.test_data: TestData = test_data

    def run(self) -> None:
        """start code interpretation"""
        n = self.test_data.sample_count
        for i in range(0, n):
            print(f"--- starting simulator for sample {i+1} of {n} ---")
            self.test_data.active_idx = i
            print("INPUT:")
            print("TODO: show input values here")
            self.run_node(self.program)
            # show output
            print("Simulator stopped successfully.")
            print("OUTPUT:")
            out = self.get_output_addresses()
            for o in out:
                print(f"{o.ident}={o.value.custom_str(False)}")

    def run_node(self, node: Node) -> Node:
        """interpret node recursively"""
        result: Node = None
        match node.ident:
            case "program":
                self.__program(node)
            case "statements":
                self.__statements(node)
            case "if":
                self.__if(node)
            case "var":
                result = self.__var(node)
            case "assign":
                result = self.__assign(node)
            case "const":
                result = self.__const(node)
            case _:
                self.__error(
                    node, f"Interpretation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
                result = None
        return result

    def __program(self, node: Node) -> None:
        """interprets a program-node"""
        self.set_input_address_values(node)
        statements = node.children[1]
        self.run_node(statements)

    def __statements(self, node: Node) -> None:
        """interprets a statements-node"""
        for child in node.children:
            self.run_node(child)

    def __if(self, node: Node) -> None:
        """interprets an if-node"""
        condition = node.children[0]
        predicate = self.run_node(condition)
        if predicate.ident == "1":
            if_true = node.children[1]
            self.run_node(if_true)
        else:
            if_false = node.children[2]
            self.run_node(if_false)

    def __assign(self, node: Node) -> Node:
        """interprets an assign-node"""
        lhs = node.children[0]
        sym = node.get_symbol(lhs.children[0].ident)
        rhs = self.run_node(node.children[1])
        sym.value = rhs
        return rhs

    def __const(self, node: Node) -> Node:
        """interprets a const-node"""
        n = node.children[0].clone()
        n.data_type = node.data_type
        return n

    def __var(self, node: Node) -> Node:
        """interprets a var-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident)
        n = sym.value.clone()  # TODO: depends on pointer or not, ...
        n.data_type = sym.data_type
        return n

    def set_input_address_values(self, node: Node) -> None:
        """sets the I/O test values to the currents node symbols"""
        for sym in node.symbols.values():
            if sym.address is None:
                continue
            addr_str = str(sym.address)
            if addr_str in self.test_data.data:
                v = self.test_data.data[addr_str][self.test_data.active_idx]
                sym.value = Node(f"{v}", -1, -1, [])

    def get_output_addresses(self) -> List[Sym]:
        """gets output addresses"""
        if self.program is None:
            return []
        result: List[Sym] = []
        for output in self.program.symbols.values():
            if (
                output.address is not None
                and output.address.direction == AddressDirection.OUTPUT
            ):
                result.append(output)
        return result

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
