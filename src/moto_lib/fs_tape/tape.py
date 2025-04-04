"""
File system on tape.
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

from .block import TapeBlock

startOfBlockSequenceToRead = b"\x01\x01\x01\x3c\x5a"
startOfBlockSequenceToWrite = (
    b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a"
)


class Tape:
    def __init__(self, rawData=None):
        self.rawData = rawData if rawData is not None else bytearray(21 * 1024)
        self._position = 0
        self.maxPosition = len(self.rawData)

    @property
    def position(self):
        return self._position

    def nextBlock(self) -> TapeBlock:
        pos = self.rawData.find(startOfBlockSequenceToRead, self.position)
        if pos == -1:
            self._position = self.maxPosition
            return None
        else:
            self._position = pos + len(startOfBlockSequenceToRead)
            if self._position + 2 <= self.maxPosition:
                length = self.rawData[self._position + 1]
                blockEnd = (
                    self._position + length + 1 if length > 0 else self._position + 257
                )
                blocRawData = self.rawData[self._position : blockEnd]
                self._position = blockEnd
                return TapeBlock(blocRawData)

    def writeBlock(self, block: TapeBlock):
        position = self._position
        nextPosition = position + len(startOfBlockSequenceToWrite)
        if nextPosition >= self.maxPosition:
            raise OverflowError("Reached end of tape.")
        self.rawData[position:nextPosition] = startOfBlockSequenceToWrite
        position = nextPosition
        nextPosition = position + len(block.rawData)
        if nextPosition >= self.maxPosition:
            raise OverflowError("Reached end of tape.")
        self.rawData[position:nextPosition] = block.rawData
        self._position = nextPosition
