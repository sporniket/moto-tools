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

from .consts import TypeOfTapeBlock


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
