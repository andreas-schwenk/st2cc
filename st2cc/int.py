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
from typing import Dict, List

from st2cc.ast import Node
from st2cc.sym import Symbol


class Sample:
    """sample data with value for each signal"""

    def __init__(self):
        self.data: Dict[str, int] = {}


class TestData:
    """Test data"""

    def __init__(self) -> None:
        self.pos: int = 0
        self.samples: List[Sample] = []

    def import_data(self, data: Dict[str, any]) -> None:
        """import TOML data"""
        # get the number of samples
        n = 0
        for ident, arr in data.items():
            n = max(n, len(arr))
        # create samples
        for _ in range(0, n):
            self.samples.append(Sample())
        # fill samples; non-specified entries are set to zero
        for ident, arr in data.items():
            for i in range(0, n):
                if i < len(arr):
                    self.samples[i].data[ident.upper()] = arr[i]
                else:
                    self.samples[i].data[ident.upper()] = 0


class Interpreter:
    """ST intermediate code interpretation"""

    def __init__(self, root: Node, config: dict[str, any]) -> None:
        self.root: Node = root
        self.config: dict[str, any] = config
        self.cycle: int = 0
        self.test_data: TestData = TestData()
        if "test" in config:
            self.test_data.import_data(config["test"])

    def run(self) -> None:
        """start code interpretation"""
        n = len(
            self.test_data.samples
        )  # TODO: support run, if no input address is given as test data (this is the case, if no address is given at all)
        for i in range(0, n):
            print(f"--- Running cycle {i+1} of {n} ---")
            self.cycle = i
            program = self.root.get_symbols("program")[0].code
            self.handle_io(program, True)  # sets the input for addresses
            self.show_io(program, "i")
            self.run_node(self.root)
            self.show_io(program, "q")
            self.handle_io(program, False)  # asserts the output for addresses
        print("... Simulator stopped successfully.")

    def run_node(self, node: Node) -> Node:
        """interpret node recursively"""
        result: Node = None
        match node.ident:
            case "file":
                self.__file(node)
            case "program":
                self.__program(node)
            case "statements":
                self.__statements(node)
            case "if":
                self.__if(node)
            case "variable":
                result = self.__variable(node)
            case "assign":
                result = self.__assign(node)
            case "add" | "sub" | "mul":
                result = self.__bin_op(node)
            case "or":
                result = self.__or(node)
            case "and":
                result = self.__and(node)
            case "leq" | "geq" | "lt" | "gt":
                result = self.__cmp(node)
            case "const":
                result = self.__const(node)
            case "call":
                result = self.__call(node)
            case _:
                msg = f"Interpretation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                self.__error(node, msg)
        return result

    def __file(self, node: Node) -> None:
        """interprets file-node"""
        program = node.get_symbols("program")[0].code
        self.run_node(program)

    def __program(self, node: Node) -> None:
        """interprets program-node"""
        statements = node.children[1]
        self.run_node(statements)

    def __statements(self, node: Node) -> None:
        """interprets statements-node"""
        for child in node.children:
            self.run_node(child)

    def __if(self, node: Node) -> None:
        """interprets if-node"""
        condition = node.children[0]
        predicate = self.run_node(condition)
        if Node.compare(predicate, Node.create_const_bool(True)):
            if_true = node.children[1]
            self.run_node(if_true)
        else:
            if_false = node.children[2]
            self.run_node(if_false)

    def __assign(self, node: Node) -> Node:
        """interprets assign-node"""
        lhs = node.children[0]
        sym = node.get_symbol(lhs.children[0].ident)  # TODO: check scope of sym
        rhs = self.run_node(node.children[1])
        sym.value = rhs
        return rhs

    def __bin_op(self, node: Node) -> Node:
        """interprets binary-operation-node"""
        op = node.ident
        o1 = self.run_node(node.children[0])
        o2 = self.run_node(node.children[1])
        res = Node.create_nil()
        if o1.data_type.ident == "int" and o2.data_type.ident == "int":
            v1 = int(o1.children[0].ident)
            v2 = int(o2.children[0].ident)
            match op:
                case "add":
                    res = Node.create_const_int(v1 + v2)
                case "sub":
                    res = Node.create_const_int(v1 - v2)
                case "mul":
                    res = Node.create_const_int(v1 * v2)
                case _:
                    self.__error(node, f"interpreter: unimplemented operation {op}")
        else:
            t1 = o1.data_type.custom_str(False)
            t2 = o2.data_type.custom_str(False)
            msg = f"interpreter: unimplemented types {t1} and {t2} for {op}"
            self.__error(node, msg)
        return res

    def __or(self, node: Node) -> Node:
        """interprets or-node. Implemented as short-circuit evaluation"""
        o1 = self.run_node(node.children[0])
        if Node.compare(o1, Node.create_const_bool(True)):
            return Node.create_const_bool(True)
        return self.run_node(node.children[1])

    def __and(self, node: Node) -> Node:
        """interprets and-node. Implemented as short-circuit evaluation"""
        o1 = self.run_node(node.children[0])
        if Node.compare(o1, Node.create_const_bool(False)):
            return Node.create_const_bool(False)
        return self.run_node(node.children[1])

    def __cmp(self, node: Node) -> Node:
        """interprets compare-node"""
        op = node.ident
        o1 = self.run_node(node.children[0])
        o2 = self.run_node(node.children[1])
        res: Node = Node.create_nil()
        if o1.data_type.ident == "int" and o2.data_type.ident == "int":
            v1 = int(o1.children[0].ident)
            v2 = int(o2.children[0].ident)
            match op:
                case "leq":
                    res = Node.create_const_bool(v1 <= v2)
                case "geq":
                    res = Node.create_const_bool(v1 >= v2)
                case "lt":
                    res = Node.create_const_bool(v1 < v2)
                case "gt":
                    res = Node.create_const_bool(v1 > v2)
                case _:
                    self.__error(node, f"interpreter: unimplemented operation {op}")
        else:
            t1 = o1.data_type.custom_str(False)
            t2 = o2.data_type.custom_str(False)
            self.__error(
                node, f"interpreter: unimplemented types {t1} and {t2} for {op}"
            )
        return res

    def __const(self, node: Node) -> Node:
        """interprets const-node"""
        return node.clone()

    def __call(self, node: Node) -> Node:
        """interprets call-node"""
        ident = node.children[0].ident
        args = node.children[1].children
        fun = node.get_symbol(ident, "function")
        params: List[Symbol] = []
        for key, value in fun.code.symbols.items():
            if value.scope == "parameter":
                params.append(value)
        # backup symbol values to simulate stack
        bak = {}
        for key, value in fun.code.symbols.items():
            bak[key] = value
        # set arguments
        n = len(params)
        for i in range(0, n):
            param = params[i]
            arg = self.run_node(args[i])
            fun.code.symbols[param.ident].value = arg
        statements = fun.code.children[2]
        self.run_node(statements)
        # restore symbol values to simulate stack
        for key, value in bak.items():
            fun.code.symbols[key] = value
        # get return value and return it
        res = fun.code.symbols[ident].value
        return res

    def __variable(self, node: Node) -> Node:
        """interprets variable-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident)
        n = sym.value.clone()  # TODO: depends on pointer or not, ...
        n.data_type = sym.data_type
        return n

    def handle_io(self, program: Node, set_input: bool) -> None:
        """sets the I/O test values to the currents node symbols, or asserts the output"""
        assert program.ident == "program"
        for sym in program.symbols.values():
            if sym.address is None:
                continue
            addr_str = str(sym.address)
            addr_bit = -1
            if "." in addr_str:  # TODO: this is just a hack...
                [addr_str, addr_bit] = addr_str.split(".")
                addr_bit = int(addr_bit)
            sample = self.test_data.samples[self.cycle]
            if addr_str in sample.data:
                value = sample.data[addr_str]
                if addr_bit >= 0:
                    value = (value >> addr_bit) & 1
                value_node = Node.create_nil()
                match sym.data_type.ident:
                    case "bool":
                        value_node = Node.create_const_bool(value != 0)
                    case "int":
                        value_node = Node.create_const_int(value)
                    case _:
                        print("ERROR: unimplemented set_input_address_values(..)")
                        sys.exit(-1)
                if set_input and sym.address.dir == "i":
                    sym.value = value_node
                elif not set_input and sym.address.dir == "q":
                    actual = sym.value
                    expected = value_node
                    if not Node.compare(actual, expected):
                        print(
                            f"ERROR: assert failed for output address '{sym.address}'!"
                        )
                        print(f"Expected value: {Node.custom_str(expected, False)}")
                        print(f"Actual value: {Node.custom_str(actual, False)}")
                        sys.exit(0)

    def show_io(self, program: Node, direction: str) -> None:
        """shows i/o address values"""
        assert program.ident == "program"
        print("INPUT:" if direction == "i" else "OUTPUT:")
        for symbol in program.symbols.values():
            if symbol.address is not None and symbol.address.dir == direction:
                print(f"  {symbol.ident}={symbol.value.brackets_str()}")

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
