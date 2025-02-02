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
from st2cc.adr import Address
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
            case "function":
                code = self.__function(node)
            case "statements":
                code = self.__statements(node)
            case "if":
                code = self.__if(node)
            case "add" | "sub" | "mul" | "or" | "and" | "leq" | "geq" | "lt" | "gt":
                code = self.__bin_op(node)
            case "variable":
                code = self.__variable(node)
            case "assign":
                code = self.__assign(node, is_statement)
            case "const":
                code = self.__const(node)
            case "call":
                code = self.__call(node)
            case _:
                self.__error(
                    node, f"Generation: UNIMPLEMENTED NODE TYPE '{node.ident}'"
                )
        return code

    def __file(self, node: Node) -> str:
        code = ""
        functions = node.get_symbols("function")
        for function in functions:
            code += self.run_node(function.code)
        program = node.get_symbols("program")[0].code
        code += self.run_node(program)
        return code

    def __program(self, node: Node) -> str:
        """generates program-node"""
        code = ""
        code += self.generate_addr_defines(node) + "\n"
        code += "int main(int argc, char *argv[]) {\n"
        code += self.indentation(self.generate_variables(node))
        code += "    while (1) {\n"
        code += self.indentation(self.generate_read_io(node), 2)
        code += self.indentation(self.run_node(node.children[1]), 2)
        code += self.indentation(self.generate_write_io(node), 2)
        code += "    }\n"  # end of while(1)
        code += "    return 0;\n"  # end of main(..)
        code += "}\n"
        return code

    def __function(self, node: Node) -> str:
        ident = node.children[0].ident
        return_type = self.generate_type(node.data_type)
        params = node.get_symbols("parameter")
        code = ""
        n = len(params)
        for i in range(0, n):
            param = params[i]
            param_type = self.generate_type(param.data_type)
            if i > 0:
                code += ", "
            code += f"{param_type} {param.ident}"
        code = f"{return_type} {ident}({code})" + " {\n"
        body = self.run_node(node.children[2])
        code += self.indentation(body)
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
        code += self.indentation(if_true)
        code += "} else {\n"
        if_false = self.run_node(node.children[2])
        code += self.indentation(if_false)
        code += "}\n"
        return code

    def __bin_op(self, node: Node) -> str:
        """generates an binary operation node"""
        op = node.ident
        o1 = self.run_node(node.children[0])
        o2 = self.run_node(node.children[1])
        code = ""
        # TODO: parentheses, based on o1, o2!!
        match op:
            case "add":
                code = f"({o1} + {o2})"
            case "sub":
                code = f"({o1} - {o2})"
            case "mul":
                code = f"({o1} * {o2})"
            case "and":
                code = f"({o1} && {o2})"
            case "or":
                code = f"({o1} || {o2})"
            case "lt":
                code = f"({o1} < {o2})"
            case "gt":
                code = f"({o1} > {o2})"
            case "leq":
                code = f"({o1} <= {o2})"
            case "geq":
                code = f"({o1} >= {o2})"
            case _:
                self.__error(node, f"unimplemented binary-operation {op}")
        return code

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
        code = node.children[0].brackets_str()
        return code

    def __call(self, node: Node) -> str:
        args = node.children[1].children
        code = ""
        n = len(args)
        for i in range(0, n):
            arg = self.run_node(args[i])
            if i > 0:
                code += ", "
            code += arg
        fun_id = node.children[0].ident
        code = f"{fun_id}({code})"
        return code

    def generate_addr_defines(self, node: Node) -> str:
        """generate defines for addresses"""
        code = ""
        for direction in ["i", "q"]:
            addr_list = filter_distinct_addr_bytes(filter_addr(node, direction))
            physical_addr = 1000 if direction == "i" else 2000
            if "addr" in self.config:
                if direction == "i" and "input" in self.config["addr"]:
                    physical_addr = self.config["addr"]["input"]
                if direction == "q" and "output" in self.config["addr"]:
                    physical_addr = self.config["addr"]["output"]
            for addr in addr_list:
                code += f"#define ADDR_{direction.upper()}{addr.pos[0]} {hex(physical_addr)}\n"
                physical_addr += addr.get_num_bytes()
        return code

    def generate_variables(self, node: Node) -> str:
        """generates IO variables and local variables"""
        code = ""
        for direction in ["i", "q"]:
            addr_list = filter_distinct_addr_bytes(filter_addr(node, direction))
            for addr in addr_list:
                bits = 8 if addr.bits == 1 else addr.bits
                code += f"uint{bits}_t {direction.upper()}{addr.pos[0]};\n"
        for sym in node.symbols.values():
            t = self.generate_type(sym.data_type)
            code += f"{t} {sym.ident};\n"
        return code

    def generate_read_io(self, node: Node) -> str:
        """generates code to read IO variables"""
        code = ""
        # read sensor data from address
        addr_list = filter_distinct_addr_bytes(filter_addr(node, "i"))
        for addr in addr_list:
            p = addr.pos[0]
            bits = 8 if addr.bits == 1 else addr.bits
            t = f"uint{bits}_t"
            code += f"i{p} = *(volatile {t} *)ADDR_I{p};\n"
        # read to variables
        for sym in node.symbols.values():
            addr = sym.address
            if addr is None or addr.dir != "i":
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
        addr_list = filter_distinct_addr_bytes(filter_addr(node, "q"))
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

    def generate_type(self, data_type: Node) -> str:
        """generates data type"""
        code = ""
        # TODO: handle pointers, arrays, ...
        match data_type.ident:
            case "bool":
                code = "bool"
                self.standard_includes.add("stdbool.h")
            case "int":
                code = "int"
            case _:
                t = data_type.ident
                print(f"ERROR: generate_type(..): UNIMPLEMENTED type '{t}'")
                sys.exit(-1)
        return code

    def indentation(self, code: str, cnt: int = 1) -> str:
        """indents code by 4 spaces"""
        ws = "    " * cnt
        return "\n".join(map(lambda line: ws + line, code.splitlines())) + "\n"

    def __error(self, node: Node, msg: str) -> None:
        """error handling"""
        print(f"ERROR:{node.row}:{node.col}:{msg}")
        sys.exit(-1)
