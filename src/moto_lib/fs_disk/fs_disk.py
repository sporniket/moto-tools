"""
File system on disk.
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
from enum import Enum
from typing import List


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


# ASSESS USEFULLNESS
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


# ASSESS USEFULLNESS
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
        blockchain: List[int],
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


# ASSESS USEFULLNESS
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


######################################################## BEGIN HERE
# private shorthand values
_SIZE_OF_SECTOR_DD = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE.sizeOfSector()
_SIZE_OF_SECTOR_SDDRIVE = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE.sizeOfSector()
_FILLER_SDDRIVE = 0xFF

#### =====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====
## Extraction des données disques


class DiskSector:
    ###
    # We will work either with Double Density sectors, or SDDrive sectors
    #
    SIZE_OF_SECTOR_DD = _SIZE_OF_SECTOR_DD  # we will work with double density image
    SIZE_OF_SECTOR_SDDRIVE = _SIZE_OF_SECTOR_SDDRIVE  # original sector filled with padding value to match SD Card sector size
    FILLER_FDDRIVE = 0xE5  # seems to be the value written by a floppy drive when low-level formatting.

    ###
    # SDDrive sectors are just normal sectors embedded in a SD Card sector.
    #
    FILLER_SDDRIVE = _FILLER_SDDRIVE  # used to fill spacing data
    SDDRIVE_PADDING_DD = bytes(
        [_FILLER_SDDRIVE for i in range(_SIZE_OF_SECTOR_SDDRIVE - _SIZE_OF_SECTOR_DD)]
    )  # padding to add after sector data

    @staticmethod
    def sizeOfSector(typeOfDiskImage: TypeOfDiskImage):
        return typeOfDiskImage.sizeOfSector()  ## thus duplicate of the enum method...

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        # always use self._sizeOfPayload for the day there is simple density.
        self._sizeOfPayload = DiskSector.SIZE_OF_SECTOR_DD
        self._typeOfDiskImage = typeOfDiskImage
        self._sizeOfSector = DiskSector.sizeOfSector(typeOfDiskImage)

        if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE:
            self._padding = None
        else:
            self._padding = DiskSector.SDDRIVE_PADDING_DD

        # Only takes care of the floppy sector, without filling data for sddrive.
        if len(rawData) < self._sizeOfPayload:
            self._data = bytearray(
                [DiskSector.FILLER_FDDRIVE for i in range(self._sizeOfPayload)]
            )
            self._data[: len(rawData)] = rawData
        else:
            self._data = bytearray(rawData[: self._sizeOfPayload])

    @property
    def data(self) -> bytes:
        return (
            bytes(self._data)
            if self._typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE
            else bytes(self._data + self._padding)
        )

    @data.setter
    def data(self, rawData: bytearray or bytes):
        # Only takes care of the floppy sector, without filling data for sddrive.
        if len(rawData) < self._sizeOfPayload:
            self._data[: len(rawData)] = rawData
        else:
            self._data = bytearray(rawData[: self._sizeOfPayload])

    def erase(self):
        self._data[:] = bytearray(
            [DiskSector.FILLER_FDDRIVE for i in range(self._sizeOfPayload)]
        )

    def asBlockAllocationTable(self) -> List[BlocAllocation]:
        usefullData = self._data[1:161]
        return [BlocAllocation(i, usefullData[i]) for i in range(0, 160)]

    def asCatalogEntries(self, bat: List[BlocAllocation]) -> List[CatalogEntry]:
        usefullData = self._data[0 : DiskSector.SIZE_OF_SECTOR_DD]
        result = []
        for i in range(0, DiskSector.SIZE_OF_SECTOR_DD, 32):
            entryData = usefullData[
                i : i + 16
            ]  # the last 16 bytes of a 32-bytes long slice are unused
            if entryData[0] == 0xFF:
                continue
            # build the list of occupied blocks
            firstBlockId = entryData[13]
            firstBlock = bat[firstBlockId]
            blockchain = [firstBlock]
            currentBlock = firstBlock
            while currentBlock.hasNext:
                currentBlock = bat[currentBlock.status]
                if currentBlock.id in [b.id for b in blockchain]:
                    # TODO emit error event
                    break  # loop detected
                if currentBlock.free:
                    # TODO emit error event
                    break  #
                blockchain += [currentBlock]
            result += [
                CatalogEntry(
                    NameOfFile(entryData[0:8], entryData[8:11]),
                    TypeOfDiskFile.fromInt(entryData[11]),
                    TypeOfData.fromByte(entryData[12]),
                    firstBlock,
                    blockchain,
                    currentBlock.usage,
                    entryData[14] * 256 + entryData[15],
                )
            ]
        return result


class DiskTrack:
    SECTORS_PER_TRACK = 16

    @staticmethod
    def sizeOfTrack(sizeOfSector: int):
        return DiskTrack.SECTORS_PER_TRACK * sizeOfSector

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        self._sizeOfSector = _sizeOfSector = DiskSector.sizeOfSector(typeOfDiskImage)
        self._sizeOfTrack = _sizeOfTrack = DiskTrack.sizeOfTrack(_sizeOfSector)
        self._typeOfDiskImage = typeOfDiskImage
        dataSize = len(rawData)

        if dataSize == 0:
            self._sectors = [
                DiskSector(typeOfDiskImage=typeOfDiskImage)
                for i in range(DiskTrack.SECTORS_PER_TRACK)
            ]
        elif dataSize >= _sizeOfTrack:
            self._sectors = [
                DiskSector(
                    rawData[(i * _sizeOfSector) : ((i + 1) * _sizeOfSector)],
                    typeOfDiskImage=typeOfDiskImage,
                )
                for i in range(DiskTrack.SECTORS_PER_TRACK)
            ]
        else:
            raise ValueError(
                f"Non empty rawData should have a length of {_sizeOfTrack} bytes for {typeOfDiskImage.name}, got {dataSize}"
            )

    @property
    def sectors(self):
        return [self._sectors[i] for i in range(DiskTrack.SECTORS_PER_TRACK)]

    def write(self, rawData: bytearray or bytes):
        dataSize = len(rawData)
        if dataSize < self._sizeOfTrack:
            raise ValueError(
                f"rawData should have a length of {self._sizeOfTrack} bytes for {self._typeOfDiskImage.name}, got {dataSize}"
            )

        for i, sector in enumerate(self._sectors):
            sector.data = rawData[
                (i * self._sizeOfSector) : ((i + 1) * self._sizeOfSector)
            ]

    def rawData(self):
        result = bytearray(self._sizeOfTrack)
        for index, sector in enumerate(self._sectors):
            result[
                index * self._sizeOfSector : (index + 1) * self._sizeOfSector
            ] = sector.data
        return bytes(result)


class DiskSide:
    # expected size of a side depending of the type of disk image
    SIZE_OF_SIDE = [327680, 655360]
    TRACKS_PER_SIDE = 80

    @staticmethod
    def sizeOfSide(sizeOfTrack: int):
        return DiskSide.TRACKS_PER_SIDE * sizeOfTrack

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        self._sizeOfSector = _sizeOfSector = DiskSector.sizeOfSector(typeOfDiskImage)
        self._sizeOfTrack = _sizeOfTrack = DiskTrack.sizeOfTrack(_sizeOfSector)
        self._sizeOfSide = _sizeOfSide = DiskSide.sizeOfSide(_sizeOfTrack)
        dataSize = len(rawData)

        if dataSize == 0:
            self._tracks = [
                DiskTrack(typeOfDiskImage=typeOfDiskImage)
                for i in range(DiskSide.TRACKS_PER_SIDE)
            ]
        elif dataSize >= _sizeOfSide:
            self._tracks = [
                DiskTrack(
                    rawData[i * _sizeOfTrack : (i + 1) * _sizeOfTrack],
                    typeOfDiskImage=typeOfDiskImage,
                )
                for i in range(DiskSide.TRACKS_PER_SIDE)
            ]
        else:
            raise ValueError(
                f"Non empty rawData should have a length of {_sizeOfSide} bytes for {typeOfDiskImage.name}, got {dataSize}"
            )

        # scan Block Allocation Table and catalog
        self._bat = self._tracks[20].sectors[1].asBlockAllocationTable()
        self._catalog = []
        for i in range(2, 16):
            self._catalog += self._tracks[20].sectors[i].asCatalogEntries(self._bat)

    @property
    def tracks(self):
        return [self._tracks[i] for i in range(DiskSide.TRACKS_PER_SIDE)]

    @property
    def size(self):
        return self._sizeOfSide

    @property
    def listOfFiles(self) -> List[str]:
        length = len(self._catalog)
        return (
            [self._catalog[i].line_catalogue for i in range(0, length)]
            if length > 0
            else []
        )


class DiskImage:
    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        # * whether it is an emulator or sddrive image
        #   * check length validity (emulator : integer multiple of base size ; sddrive : fixed size)
        #   * assess number of side (emulator : 2 or 4 ; sddrive : 4 )
        #   * instanciate each disk sides
        self._sides = sides = []  # TODO
        startPoint = 0

        for i in range(0, 4):  # up to 4 sides should be instantiated
            sides.append(DiskSide(rawData[startPoint:], typeOfDiskImage))
            startPoint = startPoint + sides[i].size
        pass

        numberOfSides = len(sides)
        if (
            typeOfDiskImage == TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
            and numberOfSides < 4
        ):
            raise ValueError(
                f"SDDrive images MUST embed 4 disk sides, got {numberOfSides}."
            )

    @property
    def sides(self) -> List[DiskSide]:
        return self._sides
