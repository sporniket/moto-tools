"""
@Since v0.0.4
---
(c) 2022 David SPORN
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

from moto_lib.fs_disk.image import TypeOfDiskImage


### Utils to create and locate data for emulator and sddrive disk images
class ImageUtils:
    def __init__(self, type: TypeOfDiskImage):
        self._sizeOfSector = type.sizeOfSector()
        self._sizeOfTrack = 16 * self._sizeOfSector
        self._sizeOfSide = 80 * self._sizeOfTrack
        self._sizeOfImage = 4 * self._sizeOfSide

    def reserveMutable(self) -> bytearray:
        return bytearray(self._sizeOfImage)

    def startOfSector(self, side: int, track: int, sector: int) -> int:
        return (
            side * self._sizeOfSide
            + track * self._sizeOfTrack
            + sector * self._sizeOfSector
        )


class BlockAllocationTableBuilder:
    def __init__(self):
        bat = bytearray([0xFF for i in range(256)])
        bat[0] = 0
        # reserve first block (boot sector), and blocks 41 and 42 (track 20 hosting the bat and catalog)
        for i in [1, 41, 42]:
            bat[i] = 0xFE
        self._bat = bat

    def withSequenceOfBlocks(self, blocks: list[int], lastBlockUsage: int):
        for i, b in enumerate(blocks[:-1]):
            # block x is stored at bat[x+1]
            self._bat[b + 1] = blocks[i + 1]
        self._bat[blocks[-1] + 1] = 0xC0 + lastBlockUsage
        return self

    def withBlock(self, index: int, value: int):
        self._bat[index + 1] = value
        return self

    def build(self) -> bytearray:
        return self._bat
