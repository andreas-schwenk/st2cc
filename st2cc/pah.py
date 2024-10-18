"""
TODO: docs

parse helper
"""

import sys

from st2cc.sym import Address, AddressDirection


def parse_address(data: str) -> Address:
    """parses the address"""
    addr = Address()
    # direction
    if data.startswith("I"):
        addr.dir = AddressDirection.INPUT
        data = data[1:]
    elif data.startswith("Q"):
        addr.dir = AddressDirection.OUTPUT
        data = data[1:]
    else:
        print("unexpected error while parsing the address")  # TODO
        sys.exit(-1)
    # number of bits
    if data.startswith("X"):
        addr.bits = 1
        data = data[1:]
    elif data.startswith("B"):
        addr.bits = 8
        data = data[1:]
    elif data.startswith("W"):
        addr.bits = 16
        data = data[1:]
    elif data.startswith("D"):
        addr.bits = 32
        data = data[1:]
    # position
    addr.pos = list(map(int, data.split(".")))
    return addr
