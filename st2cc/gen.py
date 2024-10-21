"""
gen.py

Description:
    Generation of C code.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

import sys

from st2cc.ast import Node
from st2cc.sym import Address, AddressDirection, DataType, BaseType
from st2cc.asf import filter_addr, filter_distinct_addr_bytes


class CodeGenerator:
    """C Code generation"""

    def __init__(self, root: Node, config: dict[str, any], verbose: bool) -> None:
        self.verbose: bool = verbose
        self.root: Node = root
        self.config: dict[str, any] = config
        self.standard_includes = {"inttypes.h"}

    def run(self) -> str:
        """run code generation"""
        code = ""
        code += "// This file was generated automatically by st2cc.\n"
        code += "// Visit github.com/andreas-schwenk/st2cc\n"
        code += "\n"
        core = self.run_node(self.root)
        for incl in sorted(self.standard_includes):
            code += f"#include <{incl}>\n"
        code += f"\n{core}"
        if self.verbose:
            print("----- GENERATED C CODE -----")
            print(code)
        return code

    def run_node(self, node: Node, is_statement=False) -> str:
        """generates node recursively"""
        code = ""
        match node.ident:
            case "file":
                code = self.__file(node)
            case "program":
                code = self.__program(node)
            case "statements":
                code = self.__statements(node)
            case "if":
                code = self.__if(node)
            case "or":
                code = self.__or(node)
            case "and":
                code = self.__and(node)
            case "variable":
                code = self.__variable(node)
            case "assign":
                code = self.__assign(node, is_statement)
            case "const":
                code = self.__const(node)
            case _:
                self.__error(
                    node, f"Generation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
        return code

    def __file(self, node: Node) -> str:
        program = node.get_children("program")[0]
        return self.run_node(program)

    def __program(self, node: Node) -> str:
        """generates program-node"""
        code = ""
        code += self.generate_addr_defines(node) + "\n"
        code += "int main(int argc, char *argv[]) {\n"
        code += self.indent(self.generate_variables(node))
        code += "    while (1) {\n"
        code += self.indent(self.generate_read_io(node), 2)
        code += self.indent(self.run_node(node.children[1]), 2)
        code += self.indent(self.generate_write_io(node), 2)
        code += "    }\n"  # end of while(1)
        code += "    return 0;\n"  # end of main(..)
        code += "}\n"
        return code

    def __statements(self, node: Node) -> str:
        """generates statements-node"""
        code = ""
        for child in node.children:
            code += self.run_node(child, True)
        return code

    def __if(self, node: Node) -> str:
        """generates if-node"""
        condition = self.run_node(node.children[0])
        code = f"if ({condition}) {{\n"
        if_true = self.run_node(node.children[1])
        code += self.indent(if_true)
        code += "} else {\n"
        if_false = self.run_node(node.children[2])
        code += self.indent(if_false)
        code += "}\n"
        return code

    def __or(self, node: Node) -> str:
        """generates or-node"""
        o1 = self.run_node(node.children[0])
        o2 = self.run_node(node.children[1])
        return f"({o1} || {o2})"  # TODO: parentheses, based on o1, o2!!

    def __and(self, node: Node) -> str:
        """generates and-node"""
        o1 = self.run_node(node.children[0])
        o2 = self.run_node(node.children[1])
        return f"({o1} && {o2})"  # TODO: parentheses, based on o1, o2!!

    def __variable(self, node: Node) -> str:
        """generates variable-node"""
        ident = node.children[0].ident
        sym = node.get_symbol(ident)
        return sym.ident

    def __assign(self, node: Node, is_statement=False) -> str:
        """generates assign-node"""
        code = ""
        lhs = self.run_node(node.children[0])
        rhs = self.run_node(node.children[1])
        code = f"{lhs} = {rhs}"
        if is_statement:
            code += ";\n"
        return code

    def __const(self, node: Node) -> str:
        """generates const-node"""
        code = node.const_str()
        return code

    def generate_addr_defines(self, node: Node) -> str:
        """generate defines for addresses"""
        code = ""
        for direction in [AddressDirection.INPUT, AddressDirection.OUTPUT]:
            prefix = "I" if direction == AddressDirection.INPUT else "Q"
            addr_list = filter_distinct_addr_bytes(
                filter_addr(node, AddressDirection.INPUT)
            )
            physical_addr = 1000 if direction == AddressDirection.INPUT else 2000
            if "addr" in self.config:
                if prefix == "I" and "input" in self.config["addr"]:
                    physical_addr = self.config["addr"]["input"]
                if prefix == "Q" and "output" in self.config["addr"]:
                    physical_addr = self.config["addr"]["output"]
            for addr in addr_list:
                code += f"#define ADDR_{prefix}{addr.pos[0]} {hex(physical_addr)}\n"
                physical_addr += addr.get_num_bytes()
        return code

    def generate_variables(self, node: Node) -> str:
        """generates IO variables and local variables"""
        code = ""
        for direction in [AddressDirection.INPUT, AddressDirection.OUTPUT]:
            addr_list = filter_distinct_addr_bytes(filter_addr(node, direction))
            prefix = "i" if direction == AddressDirection.INPUT else "q"
            for addr in addr_list:
                bits = 8 if addr.bits == 1 else addr.bits
                code += f"uint{bits}_t {prefix}{addr.pos[0]};\n"
        for sym in node.symbols.values():
            t = self.generate_type(sym.data_type)
            code += f"{t} {sym.ident};\n"
        return code

    def generate_read_io(self, node: Node) -> str:
        """generates code to read IO variables"""
        code = ""
        # read sensor data from address
        addr_list = filter_distinct_addr_bytes(
            filter_addr(node, AddressDirection.INPUT)
        )
        for addr in addr_list:
            p = addr.pos[0]
            bits = 8 if addr.bits == 1 else addr.bits
            t = f"uint{bits}_t"
            code += f"i{p} = *(volatile {t} *)ADDR_I{p};\n"
        # read to variables
        for sym in node.symbols.values():
            addr = sym.address
            if addr is None or addr.dir != AddressDirection.INPUT:
                continue
            p = addr.pos[0]
            shift = ""
            if addr.bits == 1 and len(addr.pos) > 1:
                shift = f" & {hex(1 << addr.pos[1])}"
            code += f"{sym.ident} = i{p}{shift};\n"
        return code

    def generate_write_io(self, node: Node) -> str:
        """generates code to write IO variables"""
        code = ""
        addr_list = filter_distinct_addr_bytes(
            filter_addr(node, AddressDirection.OUTPUT)
        )
        # write actor data to variables
        for addr in addr_list:
            p = addr.pos[0]
            c = f"q{p} = "
            first = True
            for sym in node.symbols.values():
                if Address.compare(addr, sym.address, True):
                    if not first:
                        c += " | "
                    if (
                        sym.address.bits == 1
                        and len(sym.address.pos) > 1
                        and sym.address.pos[1] != 0
                    ):
                        c += f"({sym.ident} << {sym.address.pos[1]})"
                    else:
                        c += sym.ident
                    first = False
            code += c + ";\n"
        # write to address
        for addr in addr_list:
            p = addr.pos[0]
            bits = 8 if addr.bits == 1 else addr.bits
            t = f"uint{bits}_t"
            code += f"*(volatile {t} *)ADDR_Q{p} = q{p};\n"
        return code

    def generate_type(self, dtype: DataType) -> str:
        """generates data type"""
        code = ""
        # TODO: handle pointers, arrays, ...
        match dtype.base:
            case BaseType.BOOL:
                code = "bool"
                self.standard_includes.add("stdbool.h")
            case BaseType.INT:
                code = "int"
            case _:
                print(f"ERROR: generate_type(..): UNIMPLEMENTED type '{dtype.base}'")
                sys.exit(-1)
        return code

    def indent(self, code: str, cnt: int = 1) -> str:
        """indents code by 4 spaces"""
        ws = "    " * cnt
        return "\n".join(map(lambda line: ws + line, code.splitlines())) + "\n"

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
