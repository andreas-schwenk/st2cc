"""
pah.py

Description:
    Parser helper.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

import sys

from st2cc.adr import Address


def parse_address(data: str) -> Address:
    """parses the address"""
    addr = Address()
    # direction
    if data.startswith("I"):
        addr.dir = "i"
        data = data[1:]
    elif data.startswith("Q"):
        addr.dir = "q"
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
