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

from enum import Enum, IntEnum


class TypeOfTapeBlock(IntEnum):
    LEADER = 0x00
    DATA = 0x01
    EOF = 0xFF


class TapeBlock:
    @staticmethod
    def computeChecksum(data):
        sum = 0
        for byte in data:
            sum = (sum + byte) & 0xFF
        checksum = (0x100 - sum) & 0xFF
        return checksum

    @staticmethod
    def buildFromData(data, type: TypeOfTapeBlock = TypeOfTapeBlock.DATA):
        if data is None:
            return TapeBlock(bytes([type.value, 2, 0]))
        return TapeBlock(
            bytes(
                bytes([type.value, (len(data) + 2) & 0xFF])
                + data
                + bytes([TapeBlock.computeChecksum(data)])
            )
        )

    def __init__(self, rawData, readOnly=True):
        self.rawData = rawData
        self.readOnly = readOnly

    @property
    def type(self):
        return TypeOfTapeBlock(self.rawData[0])

    @property
    def length(self):
        return 256 if self.rawData[1] == 0 else self.rawData[1]

    @property
    def checksum(self):
        return self.rawData[-1]

    @property
    def body(self):
        return self.rawData[2:-1]  # FIXME

    def isValidChecksum(self):
        return TapeBlock.computeChecksum(self.body) == self.checksum

    def isValidLength(self):
        return False if self.length == 1 else self.length == len(self.rawData) - 1

    def isValid(self):
        return self.isValidLength() and self.isValidChecksum()


class LeaderTapeBlockDescriptor:
    def __init__(self, fileName: str, fileExtension: str, fileType: int, fileMode: int):
        self.fileName = fileName  # TODO decode + trim, to upper
        self.fileExtension = fileExtension  # TODO decode + trim, to upper
        self.fileType = fileType  # Restrict to 0..255
        self.fileMode = fileMode  # Restrict to 0..65535

    @staticmethod
    def buildFromTapeBlock(rawData):
        return LeaderTapeBlockDescriptor(
            rawData[2:10].decode("utf-8").strip(),
            rawData[10:13].decode("utf-8").strip(),
            rawData[13],
            rawData[14] * 256 + rawData[15],
        )

    def toTapeBlock(self) -> TapeBlock:
        data = bytearray(14)  # name (8), extension (3), type (1), mode (2)
        data[0:8] = (self.fileName.upper() + "        ").encode("utf-8")[0:8]
        data[8:11] = (self.fileExtension.upper() + "   ").encode("utf-8")[0:3]
        data[11] = self.fileType & 0xFF
        data[12] = (self.fileMode >> 8) & 0xFF
        data[13] = self.fileMode & 0xFF
        return TapeBlock.buildFromData(data, TypeOfTapeBlock.LEADER)


startOfBlockSequenceToRead = b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a"
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
