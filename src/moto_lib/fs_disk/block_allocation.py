"""
Block allocation.
---
(c) 2022~2024 David SPORN
---
This is part of MO/TO tools.

MO/TO tools is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

MO/TO tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with MO/TO tools.
If not, see <https://www.gnu.org/licenses/>.
---
"""

from __future__ import annotations
from enum import Enum


class BlockStatus(Enum):
    """A list of values to be used as range limit or special values."""

    MIN_NEXT = 0
    MAX_NEXT = 160  # For 80 tracks
    LAST_BLOCK = 192  # 0b11000000
    MIN_LAST = 193
    MAX_LAST = 201
    RESERVED = 0xFE
    FREE = 0xFF

    @staticmethod
    def isValidStatus(value: int) -> bool:
        return (
            False
            if (
                value >= BlockStatus.MAX_NEXT.value
                and value < BlockStatus.MIN_LAST.value
            )
            or (
                value >= BlockStatus.MAX_LAST.value
                and value < BlockStatus.RESERVED.value
            )
            else True
        )


class BlockAllocation:
    def __init__(self, id: int, status: int = BlockStatus.FREE.value):
        if not BlockStatus.isValidStatus(status):
            raise ValueError(f"block.allocation.status.is.wrong:{status}")
        self._status = status
        self._id = id

    @property
    def id(self) -> int:
        return self._id

    @property
    def status(self) -> int:
        return self._status

    @property
    def usage(self):
        return (
            0
            if self.isFree()
            else (
                8
                if self.isReserved() or self.hasNext()
                else (self._status - BlockStatus.LAST_BLOCK.value) if self.isLast else 0
            )
        )

    def isFree(self) -> bool:
        return self._status == BlockStatus.FREE.value

    def isReserved(self) -> bool:
        return self._status == BlockStatus.RESERVED.value

    def isLast(self) -> bool:
        return (
            self._status > BlockStatus.LAST_BLOCK.value
            and self._status < BlockStatus.MAX_LAST.value
        )

    def hasNext(self) -> bool:
        return self._status < BlockStatus.MAX_NEXT.value

    def setFree(self):
        self._status = BlockStatus.FREE.value

    def reserve(self):
        self._status = BlockStatus.RESERVED.value

    def linkTo(self, target: int | BlockAllocation):
        if isinstance(target, BlockAllocation):
            if target.id not in range(160):
                raise ValueError(f"id.out.of.range:{target.id}")
            self._status = target.id
        elif isinstance(target, int):
            if target not in range(160):
                raise ValueError(f"id.out.of.range:{target}")
            self._status = target

    def setupAsLastBlock(self, usage: int):
        if usage not in range(1, 9):
            raise ValueError(f"usage.out.of.range:{usage}")
        self._status = 0xC0 + usage
