"""
adr.py

Description:
    I/O address handling.

Author:
    Andreas Schwenk (schwenk@member.fsf.org)

License:
    GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
"""

from __future__ import annotations

from typing import List


class Address:
    """Address for I/O"""

    def __init__(self) -> None:
        self.dir: str = "i"  # i := input, q := output
        self.bits: int = 1
        self.pos: List[int] = [0]

    @staticmethod
    def compare(u: Address, v: Address, cmp_only_pos_0: bool = False) -> bool:
        """compares two addresses"""
        if u.dir != v.dir:
            return False
        if u.bits != v.bits:
            return False
        if cmp_only_pos_0 and u.pos[:1] != v.pos[:1]:
            return False
        if not cmp_only_pos_0 and u.pos != v.pos:
            return False
        return True

    def get_num_bytes(self) -> int:
        """returns the number of bytes"""
        return self.bits // 8

    def get_byte_pos(self) -> int:
        """returns the position of the first byte"""
        if len(self.pos == 0):
            return 0
        return max(1, self.get_num_bytes()) * self.pos[0]

    def __str__(self) -> str:
        s = self.dir.upper()
        s += {1: "X", 8: "B", 16: "W", 32: "D"}.get(self.bits)
        s += ".".join(map(str, self.pos))
        return s
