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
from .block_allocation import BlockAllocation, BlockStatus


# TYPE_OF_FILE_AS_CHAR = ["B", "D", "M", "A"]
TYPE_OF_FILE_AS_CATALOG_STRING = ["BASIC", "DATA", "MODULE", "TEXT"]
# TYPE_OF_FILE_CHAR_TO_INT_MAP = {"B": 0, "D": 1, "M": 2, "A": 3}


class TypeOfDiskFile(Enum):
    BASIC_PROGRAM = 0
    BASIC_DATA = 1
    MACHINE_LANGUAGE_PROGRAM = 2
    TEXT_FILE = 3

    @classmethod
    def fromByte(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            return cls(1)  # unknown type will be basic data

    #    @classmethod
    #    def fromCharacterCode(cls, value: str):
    #        if value not in TYPE_OF_FILE_AS_CHAR:
    #            raise ValueError(f"Unknown character code '{value}'")
    #        return cls(TYPE_OF_FILE_CHAR_TO_INT_MAP[value])

    #    def toCharacterCode(self) -> str:
    #        return TYPE_OF_FILE_AS_CHAR[self.value]

    def toByte(self) -> int:
        return self.value

    def toStringForCatalog(self) -> str:
        return TYPE_OF_FILE_AS_CATALOG_STRING[self.value]


# TYPE_OF_DATA_AS_CHAR = ["B", "A"]
TYPE_OF_DATA_AS_CATALOG_STRING = ["BINARY", "ASCII"]
TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC = ["TOKEN", "ASCII"]
# TYPE_OF_DATA_CHAR_TO_INT_MAP = {"B": 0, "A": 1}


class TypeOfData(Enum):
    BINARY_DATA = 0
    ASCII_DATA = 1

    @classmethod
    def fromByte(cls, value: int):
        return TypeOfData.ASCII_DATA if value == 0xFF else TypeOfData.BINARY_DATA

    #    @classmethod
    #    def fromCharacterCode(cls, value: str):
    #        if value not in TYPE_OF_DATA_AS_CHAR:
    #            raise ValueError(f"Unknown character code '{value}'")
    #        return cls(TYPE_OF_DATA_CHAR_TO_INT_MAP[value])

    #    def toCharacterCode(self) -> str:
    #        return "B" if self.value == 0 else "A"

    def toByte(self) -> int:
        return 0 if self.value == 0 else 0xFF

    def toStringForCatalog(self, typeOfFile: TypeOfDiskFile) -> str:
        return (
            TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC[self.value]
            if typeOfFile == TypeOfDiskFile.BASIC_PROGRAM
            else TYPE_OF_DATA_AS_CATALOG_STRING[self.value]
        )


FIRST_CHAR_OF_NAME_OF_DELETED_FILE = ord("*") & 0xFF
PADDING_CHAR = 0x20
INVALID_CHAR = ord("x")
SIZE_OF_ENTRY_NAME = 8
NAME_OF_EMPTY_ENTRY = bytes([PADDING_CHAR for i in range(SIZE_OF_ENTRY_NAME)])
SIZE_OF_ENTRY_EXTENSION = 3
EXTENSION_OF_EMPTY_ENTRY = bytes([PADDING_CHAR for i in range(SIZE_OF_ENTRY_EXTENSION)])
PADDING_OF_RECORD = bytes([0xFF for i in range(16)])


class CatalogEntryRecord:
    """Representation of meaningfull data of a catalog entry"""

    @staticmethod
    def fromBytes(data: bytes | bytearray):
        """Deserialize a record from a sequence of bytes

        Args:
            data (bytes | bytearray): the sequence of bytes to deserialize from.

        Returns:
            CatalogEntryRecord: the record
        """
        return CatalogEntryRecord(
            name=data[0:8],
            extension=data[8:11],
            typeOfFile=TypeOfDiskFile.fromByte(data[11]),
            typeOfData=TypeOfData.fromByte(data[12]),
            firstBlock=data[13],
            usageOfLastSector=(data[14] << 8) + data[15],
        )

    @staticmethod
    def _bytesFromStr(s: str, size: int = 8) -> bytes:
        encoded = s.encode(encoding="ascii")
        sizeOfEncoded = len(encoded)
        if sizeOfEncoded >= size:
            return encoded[:size]
        return encoded + bytes([PADDING_CHAR for i in range(size - sizeOfEncoded)])

    def __init__(
        self,
        *,
        name: str | bytes | bytearray = NAME_OF_EMPTY_ENTRY,
        extension: str | bytes | bytearray = EXTENSION_OF_EMPTY_ENTRY,
        typeOfFile: TypeOfDiskFile = TypeOfDiskFile.BASIC_DATA,
        typeOfData: TypeOfData = TypeOfData.BINARY_DATA,
        firstBlock: int = 0xFF,
        usageOfLastSector: int = 1,
    ):
        self._data = data = bytearray(16)
        if isinstance(name, str):
            self._data[0:8] = CatalogEntryRecord._bytesFromStr(name, SIZE_OF_ENTRY_NAME)
        else:
            _name = name[:SIZE_OF_ENTRY_NAME]
            self._data[0 : len(_name)] = _name
        if isinstance(extension, str):
            self._data[8:11] = CatalogEntryRecord._bytesFromStr(
                extension, SIZE_OF_ENTRY_EXTENSION
            )
        else:
            _extension = extension[:SIZE_OF_ENTRY_NAME]
            self._data[8 : 8 + len(_extension)] = _extension
        for i in range(11):
            if self._data[i] < 0x20:
                # non printable char
                self._data[i] = INVALID_CHAR
        self._data[11] = typeOfFile.toByte()
        self._data[12] = typeOfData.toByte()
        self._data[13] = firstBlock
        self._data[14] = (usageOfLastSector >> 8) & 0xFF
        self._data[15] = usageOfLastSector & 0xFF

    @property
    def usageOfLastSector(self) -> int:
        return (self._data[14] << 8) + self._data[15]

    @property
    def firstBlock(self) -> int:
        return self._data[13]

    def toBytes(self) -> bytes:
        return bytes(self._data + PADDING_OF_RECORD)

    def toDict(self) -> dict[str, any]:
        typeOfFile = TypeOfDiskFile.fromByte(self._data[11])
        return {
            "name": self._data[0:8].decode(encoding="ascii"),
            "extension": self._data[8:11].decode(encoding="ascii"),
            "typeOfFile": typeOfFile.toStringForCatalog(),
            "typeOfData": TypeOfData.fromByte(self._data[12]).toStringForCatalog(
                typeOfFile
            ),
        }

    def reset(self):
        """Setup internal state to clear any pre-existent data."""
        self._data[0:8] = NAME_OF_EMPTY_ENTRY
        self._data[8:11] = EXTENSION_OF_EMPTY_ENTRY
        self._data[11] = TypeOfDiskFile.BASIC_DATA.toByte()
        self._data[12] = TypeOfData.BINARY_DATA.toByte()
        self._data[13] = 0xFF
        self._data[14] = 0
        self._data[15] = 1
        pass


class CatalogEntryUsage:
    @staticmethod
    def fromBlockAllocationTable(
        bat: list[BlockAllocation], firstBlock: int, usageOfLastSector: int
    ):
        blocks = []
        _blockId = firstBlock
        _block = bat[_blockId]
        if _block.isFree() or _block.isReserved():
            return CatalogEntryUsage()
        blocks.append(_block)
        while not _block.isLast():
            _blockId = _block.status
            _block = bat[_blockId]
            if _block.isFree() or _block.isReserved():
                # something is fishy
                break
            blocks.append(_block)
        return CatalogEntryUsage(blocks=blocks, usageOfLastSector=usageOfLastSector)

    def __init__(
        self, *, blocks: list[BlockAllocation] = [], usageOfLastSector: int = 0
    ):
        self._blocks = blocks
        self._usageOfLastSector = usageOfLastSector

    def toDict(self) -> dict[str, any]:
        return (
            {
                "sizeInBlocks": len(self._blocks),
                "sizeInBytes": (
                    0
                    if len(self._blocks) == 0
                    else (8 * (len(self._blocks) - 1) + self._blocks[-1].usage - 1)
                    * 255
                    + self._usageOfLastSector
                ),
            }
            if len(self._blocks)
            else {"sizeInBlocks": 0, "sizeInBytes": 0}
        )

    def toUsageDict(self) -> dict[str, any]:
        return (
            {
                "blocks": [b.id for b in self._blocks],
                "usageOfLastBlock": self._blocks[-1].status
                - BlockStatus.LAST_BLOCK.value,
                "usageOfLastSector": self._usageOfLastSector,
            }
            if len(self._blocks)
            else {"blocks": [], "usageOfLastBlock": 0, "usageOfLastSector": 0}
        )


class CatalogEntryStatus(Enum):
    NEVER_USED = 0
    ALIVE = 1
    DELETED = 2

    @classmethod
    def fromByte(cls, value: int):
        return (
            CatalogEntryStatus.NEVER_USED
            if value == 0xFF
            else CatalogEntryStatus.DELETED if value == 0 else CatalogEntryStatus.ALIVE
        )


class CatalogEntry:
    @staticmethod
    def fromBytes(data: bytes | bytearray, bat: list[BlockAllocation]):
        """Deserialize a record from a sequence of bytes

        Args:
            data (bytes | bytearray): the sequence of bytes to deserialize from.
            bat (list[BlockAllocation]): the block allocation table to extract block usage.

        Returns:
            CatalogEntry: the catalog entry
        """
        status = CatalogEntryStatus.fromByte(data[0])
        if status == CatalogEntryStatus.NEVER_USED:
            return CatalogEntry(status)
        else:
            record = CatalogEntryRecord.fromBytes(data)
            usage = CatalogEntryUsage.fromBlockAllocationTable(
                bat, record.firstBlock, record.usageOfLastSector
            )
            return CatalogEntry(status, data=record, usage=usage)

    def __init__(
        self,
        status: CatalogEntryStatus = CatalogEntryStatus.NEVER_USED,
        *,
        data: CatalogEntryRecord = None,
        usage: CatalogEntryUsage = None,
    ):
        self._status = status
        self._data = data if data is not None else CatalogEntryRecord()
        self._usage = usage if usage is not None else CatalogEntryUsage()

    @property
    def status(self) -> CatalogEntryStatus:
        return self._status

    def toBytes(self) -> bytes:
        """Returns a 32 bytes sequence that can be put on an image disk."""
        if self._status == CatalogEntryStatus.NEVER_USED:
            return bytes([0xFF for i in range(32)])
        else:
            dataBytes = self._data.toBytes()
            return (
                dataBytes
                if self._status == CatalogEntryStatus.ALIVE
                else bytes([0]) + dataBytes[1:]
            )

    def markAsDeleted(self):
        self._status = CatalogEntryStatus.DELETED

    def reset(self):
        self._status = CatalogEntryStatus.NEVER_USED
        self._data.reset()

    def toDict(self) -> dict[str, any]:
        """Returns a representation as a dictionnary"""
        result = {"status": self._status.name}
        if self._status == CatalogEntryStatus.NEVER_USED:
            return result

        result.update(self._data.toDict())
        result.update(self._usage.toDict())
        return result

    def toUsageDict(self) -> dict[str, any] or None:
        """Returns the actual usage (block by block) of the file in the disk"""
        if self._status != CatalogEntryStatus.ALIVE:
            return None

        result = {}
        result.update(self._usage.toUsageDict())
        return result
