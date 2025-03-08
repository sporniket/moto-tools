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
from .block import TapeBlock


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
