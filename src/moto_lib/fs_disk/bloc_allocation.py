"""
Bloc allocation.
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


class BlocAllocation:
    def __init__(self, id: int, status: int = BlockStatus.FREE.value):
        if id < BlockStatus.MIN_NEXT.value or id >= BlockStatus.MAX_NEXT.value:
            raise ValueError(
                f"id should be between {BlockStatus.MIN_NEXT.value} included and {BlockStatus.MAX_NEXT.value} excluded ; got {id}."
            )
        if (
            status < BlockStatus.MIN_NEXT.value
            or (
                status >= BlockStatus.MAX_NEXT.value
                and status < BlockStatus.MIN_LAST.value
            )
            or (
                status >= BlockStatus.MAX_LAST.value
                and status < BlockStatus.RESERVED.value
            )
            or (status > BlockStatus.FREE.value)
        ):
            raise ValueError(
                f"status should be between {BlockStatus.MIN_NEXT.value} included and {BlockStatus.MAX_NEXT.value} excluded, or between {BlockStatus.MIN_LAST.value} included and {BlockStatus.MAX_LAST.value} excluded, or {BlockStatus.RESERVED.value} or {BlockStatus.FREE.value} ; got {status}."
            )
        self.id = id
        self.status = status
        self.free = status == BlockStatus.FREE.value
        self.isLastBlock = (
            status > BlockStatus.LAST_BLOCK.value
            and status < BlockStatus.MAX_LAST.value
        )
        self.usage = (
            8
            if status < BlockStatus.MAX_NEXT.value
            else status - BlockStatus.LAST_BLOCK.value
            if self.isLastBlock
            else 0
        )
        self.hasNext = status < BlockStatus.MAX_NEXT.value
