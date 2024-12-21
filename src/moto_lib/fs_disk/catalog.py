"""
Catalog.
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


class TypeOfDiskImage(Enum):
    EMULATOR_FLOPPY_IMAGE = 0
    SDDRIVE_FLOPPY_IMAGE = 1

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

    def sizeOfSector(self):
        return 256 if self == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE else 512


TYPE_OF_FILE_AS_CHAR = ["B", "D", "M", "A"]
TYPE_OF_FILE_AS_CATALOG_STRING = ["BASIC", "DATA", "MODULE", "TEXT"]
TYPE_OF_FILE_CHAR_TO_INT_MAP = {"B": 0, "D": 1, "M": 2, "A": 3}


class TypeOfDiskFile(Enum):
    BASIC_PROGRAM = 0
    BASIC_DATA = 1
    MACHINE_LANGUAGE_PROGRAM = 2
    TEXT_FILE = 3

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

    @classmethod
    def fromCharacterCode(cls, value: str):
        if value not in TYPE_OF_FILE_AS_CHAR:
            raise ValueError(f"Unknown character code '{value}'")
        return cls(TYPE_OF_FILE_CHAR_TO_INT_MAP[value])

    def asCharacterCode(self) -> str:
        return TYPE_OF_FILE_AS_CHAR[self.value]

    def asByte(self) -> int:
        return self.value


TYPE_OF_DATA_AS_CHAR = ["B", "A"]
TYPE_OF_DATA_AS_CATALOG_STRING = ["BINARY", "ASCII"]
TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC = ["TOKEN", "ASCII"]
TYPE_OF_DATA_CHAR_TO_INT_MAP = {"B": 0, "A": 1}


class TypeOfData(Enum):
    BINARY_DATA = 0
    ASCII_DATA = 1

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

    @classmethod
    def fromByte(cls, value: int):
        return TypeOfData.BINARY_DATA if value == 0 else TypeOfData.ASCII_DATA

    @classmethod
    def fromCharacterCode(cls, value: str):
        if value not in TYPE_OF_DATA_AS_CHAR:
            raise ValueError(f"Unknown character code '{value}'")
        return cls(TYPE_OF_DATA_CHAR_TO_INT_MAP[value])

    def asCharacterCode(self) -> str:
        return "B" if self.value == 0 else "A"

    def asByte(self) -> int:
        return 0 if self.value == 0 else 0xFF


class NameOfFile:
    def __init__(self, name: bytearray, suffix: bytearray):
        self._name = bytearray(
            [
                0x20,
                0x20,
                0x20,
                0x20,
                0x20,
                0x20,
                0x20,
                0x20,
            ]
        )
        self._suffix = bytearray([0x20, 0x20, 0x20])
        if len(name) <= len(self._name):
            self._name[0 : len(name)] = name
        else:
            self._name = name[0 : len(self._name)]
            self._overflow = True
            self._wanted_name = name
        if len(suffix) <= len(self._suffix):
            self._suffix[0 : len(suffix)] = suffix
        else:
            self._suffix = suffix[0 : len(self._suffix)]
            self._overflow = True
            self._wanted_suffix = suffix
        self._deleted = self._name[0] == 0
        self._free = self._name[0] == 0xFF

    @property
    def name(self):
        return self._name

    @property
    def stringFromName(self):
        return self.name.decode(encoding="ascii")

    @property
    def suffix(self):
        return self._suffix

    @property
    def stringFromSuffix(self):
        return self.suffix.decode(encoding="ascii")

    @property
    def deleted(self):
        return self._name[0] == 0

    @property
    def free(self):
        return self._name[0] == 0xFF

    @property
    def overflow(self):
        return self._wanted_name is not None or self._wanted_suffix is not None

    @property
    def wanted_name(self):
        return self._wanted_name if self.wanted_name is None else self._name

    @property
    def wanted_suffix(self):
        return self._wanted_suffix if self.wanted_suffix is None else self._suffix

    @property
    def name8dot3(self) -> str:
        return f"{self.stringFromName}.{self.stringFromSuffix}"

    @property
    def namedot(self) -> str:
        return f"{self.stringFromName.rstrip()}.{self.stringFromSuffix.rstrip()}"


# ASSESS USEFULLNESS
class CatalogEntry:
    def __init__(
        self,
        name: NameOfFile,
        typeOfFile: TypeOfDiskFile,
        typeOfData: TypeOfData,
        firstBlock: int,
        blockchain: list[int],
        usageOfLastBlock: int,
        usageOfLastSector: int,
    ):
        self.name = name
        self.typeOfFile = typeOfFile
        self.typeOfData = typeOfData
        self.firstBlock = firstBlock
        self.usageOfLastSector = usageOfLastSector
        self.usageOfLastBlock = usageOfLastBlock
        self.blockchain = blockchain

    @property
    def valid_firstBlock(self):
        return 0 <= self.firstBlock and self.firstBlock < 80

    @property
    def valid_usageOfLastSector(self):
        return 1 <= self.usageOfLastSector and self.usageOfLastSector < 256

    @property
    def valid_name(self):
        return self.name.overflow is False

    # to refactor into a rendering framework
    @property
    def line_catalogue(self) -> str:
        nameColumn = self.name.name8dot3  # (self.name.namedot + "            ")[0:13]
        typeOfFile = TYPE_OF_FILE_AS_CATALOG_STRING[self.typeOfFile.value]
        typeOfData = (
            TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC[self.typeOfData.value]
            if self.typeOfFile == TypeOfDiskFile.BASIC_PROGRAM
            else TYPE_OF_DATA_AS_CATALOG_STRING[self.typeOfData.value]
        )
        numberOfBlocks = len(self.blockchain)
        sizeOfFile = (
            (numberOfBlocks - 1) * 2048
            + 256 * (self.usageOfLastBlock - 1)
            + self.usageOfLastSector
        )
        fmtdSizeOfFile = (f" {sizeOfFile:10} octets")[-20:]
        fmtdNumberOfBlocks = (f" {numberOfBlocks:3} blocs")[-10:]
        return f"{nameColumn}\t{typeOfFile}\t{typeOfData}\t#{self.firstBlock.id:3}\t{fmtdSizeOfFile}{fmtdNumberOfBlocks}"
