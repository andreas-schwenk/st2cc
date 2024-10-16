"""
gen.py

Description:
    Generation of C code.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from typing import Set
import sys

from st2cc.ast import Node
from st2cc.sym import AddressDirection, DataType, BaseType


class CodeGenerator:
    """C Code generation"""

    def __init__(self, program: Node) -> None:
        self.program: Node = program
        self.standard_includes = {"inttypes.h"}

    def run(self) -> None:
        """start code generation"""
        code = ""
        code += "// This file was generated automatically by st2cc.\n"
        code += "// Visit github.com/andreas-schwenk/st2cc\n"
        code += "\n"
        core = self.run_node(self.program)
        for incl in sorted(self.standard_includes):
            code += f"#include <{incl}>\n"
        code += f"\n{core}"
        # TODO: only on verbose mode; write to file
        print("----- GENERATED C CODE -----")
        print(code)

    def run_node(self, node: Node, is_statement=False) -> str:
        """generates node recursively"""
        code = ""
        match node.ident:
            case "program":
                code = self.__program(node)
            case "statements":
                code = self.__statements(node)
            case "if":
                code = self.__if(node)
            case "or":
                code = self.__or(node)
            case "var":
                code = self.__var(node)
            case "assign":
                code = self.__assign(node, is_statement)
            case "const":
                code = self.__const(node)
            case _:
                self.__error(
                    node, f"Generation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
        return code

    def __program(self, node: Node) -> str:
        """generates program-node"""
        code = "int main(int argc, char *argv[]) {\n"
        code += self.indent(self.generate_io_variables(node))
        code += self.indent(self.generate_variables(node))
        code += "    while (1) {\n"
        code += self.indent(self.generate_read_io(node), 2)
        code += self.indent(self.run_node(node.children[1]), 2)
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
        return f"{o1} || {o2}"  # TODO: parentheses, based on o1, o2!!

    def __var(self, node: Node) -> str:
        """generates var-node"""
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

    def generate_io_variables(self, program: Node) -> str:
        """generates IO variables"""
        if program.ident != "program":
            print("ERROR: generate_io(..) must be applied to a 'program'")
            sys.exit(-1)
        code = ""

        # TODO: filter for addresses e.g. in ast.py -> much code is repeated
        # in this file + int.py

        for direction in [AddressDirection.INPUT, AddressDirection.OUTPUT]:
            prefix = ""
            handled: Set[int] = set()
            match direction:
                case AddressDirection.INPUT:
                    prefix = "i"
                case AddressDirection.OUTPUT:
                    prefix = "q"
            for sym in program.symbols.values():
                addr = sym.address
                if addr is None or sym.address.direction != direction:
                    continue
                if addr.position[0] in handled:
                    continue
                bits = 8 if addr.bits == 1 else addr.bits
                code += f"uint{bits}_t {prefix}{addr.position[0]};\n"
                handled.add(addr.position[0])
        return code

    def generate_read_io(self, node: Node) -> str:
        """generates code to read IO variables"""
        code = ""
        # read from address
        handled: Set[int] = set()
        for sym in node.symbols.values():
            addr = sym.address
            if addr is None or addr.direction != AddressDirection.INPUT:
                continue
            p = addr.position[0]
            if p in handled:
                continue
            bits = 8 if addr.bits == 1 else addr.bits
            t = f"uint{bits}_t"
            code += f"i{p} = *(volatile {t} *)ADDR_I{p};\n"
            handled.add(addr.position[0])
        # read to variables
        for sym in node.symbols.values():
            addr = sym.address
            if addr is None or addr.direction != AddressDirection.INPUT:
                continue
            p = addr.position[0]
            shift = ""
            if addr.bits == 1 and len(addr.position) > 1:
                shift = f" & {hex(1 << addr.position[1])}"
            code += f"{sym.ident} = i{p}{shift};\n"
        return code

    def generate_variables(self, ast: Node) -> str:
        """generates variables from symbols"""
        code = ""
        for sym in ast.symbols.values():
            t = self.generate_type(sym.data_type)
            code += f"{t} {sym.ident};\n"
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
