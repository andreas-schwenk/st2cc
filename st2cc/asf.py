"""
asf.py

Description:
    Filtering functions for the abstract syntax tree.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from typing import List, Set

from st2cc.ast import Node
from st2cc.adr import Address


def filter_addr(node: Node, addr_dir: str) -> List[Address]:
    """
    Filters a list of node symbol addresses based on direction and returns a
    modified list that meets the specified direction criteria.
    """
    res: List[Address] = []
    for sym in node.symbols.values():
        if sym.address is None or sym.address.dir != addr_dir:
            continue
        res.append(sym.address)
    return res


def filter_distinct_addr_bytes(addr_list: List[Address]) -> List[Address]:
    """only keeps one address for each first-level position"""
    res: List[Address] = []
    handled_bytes: Set[int] = set()
    for item in addr_list:
        p = item.pos[0]
        if p in handled_bytes:
            continue
        res.append(item)
        handled_bytes.add(p)
    return res
