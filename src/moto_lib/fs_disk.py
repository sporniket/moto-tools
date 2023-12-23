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
TYPE_OF_FILE_AS_STRING = ["B", "D", "M", "A"]
TYPE_OF_FILE_AS_CATALOG_STRING = ["BASIC", "DATA", "MODULE", "TEXT"]
TYPE_OF_DATA_AS_CATALOG_STRING = ["BINARY", "ASCII"]
TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC = ["TOKEN", "ASCII"]


class TypeOfDiskImage(Enum):
    EMULATOR_FLOPPY_IMAGE = 0
    SDDRIVE_FLOPPY_IMAGE = 1

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

    def sizeOfSector(self):
        return 256 if self == EMULATOR_FLOPPY_IMAGE else 512


class TypeOfFile(Enum):
    BASIC_PROGRAM = 0
    BASIC_DATA = 1
    MACHINE_LANGUAGE_PROGRAM = 2
    TEXT_FILE = 3

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

    def asCharacterCode(self) -> str:
        return TYPE_OF_FILE_AS_STRING[type.value]

    def asByte(self) -> int:
        return self.value


class TypeOfData(Enum):
    BINARY_DATA = 0
    ASCII_DATA = 1

    @classmethod
    def fromInt(cls, value: int):
        return cls(value)

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
            self._overflow = true
            self._wanted_name = name
        if len(suffix) <= len(self._suffix):
            self._suffix[0 : len(suffix)] = suffix
        else:
            self._suffix = suffix[0 : len(self._suffix)]
            self._overflow = true
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


class CatalogEntry:
    def __init__(
        self,
        name: NameOfFile,
        typeOfFile: TypeOfFile,
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

    @property
    def line_catalogue(self) -> str:
        nameColumn = (self.name.namedot + "            ")[0:13]
        typeOfFile = TYPE_OF_FILE_AS_CATALOG_STRING[self.typeOfFile.value]
        typeOfData = (
            TYPE_OF_DATA_AS_CATALOG_STRING_WHEN_BASIC[self.typeOfData.value]
            if self.typeOfData == TypeOfData.BASIC_PROGRAM
            else TYPE_OF_DATA_AS_CATALOG_STRING[self.typeOfData.value]
        )
        numberOfBlocks = len(self.blockchain)
        sizeOfFile = (
            (numberOfBlocks - 1) * 2048
            + 256 * (self.usageOfLastBlock - 1)
            + self.usageOfLastSector
        )
        fmtdSizeOfFile = (f"       {sizeOfFile} octets")[-20:]
        fmtdNumberOfBlocks = (f"    {numberOfBlocks} blocs")[-10:]
        return f"{nameColumn}\t{typeOfFile}\t{typeOfData}\t#{self.firstBlock}\t{fmtdSizeOfFile}{fmtdNumberOfBlocks}"


class BlockStatus(Enum):
    """A list of values to be used as range limit or special values."""

    MIN_NEXT = 0
    MAX_NEXT = 80
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
            or (status >= BlockStatus.MAX_LAST and status < BlockStatus.RESERVED)
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
            if status < BlockStatus.MAX_NEXT
            else status - BlockStatus.LAST_BLOCK.value
            if self.isLastBlock
            else 0
        )
        self.hasNext = status < BlockStatus.MAX_NEXT


#### =====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====
## Extraction des données disques


def extractBlockAllocationTableFromSector(
    data: bytearray or bytes,
) -> List[BlocAllocation]:
    usefullData = data[1:81]
    return [BlocAllocation(i, data[i]) for i in range(0, 80)]


def extractCatalogEntriesFromSector(
    data: bytearray or bytes, bat: List[BlocAllocation]
) -> List[CatalogEntry]:
    usefullData = data[0:256]
    result = []
    for i in range(0, 256, 32):
        entryData = usefullData[
            i : i + 16
        ]  # the last 16 bytes of a 32-bytes long slice are unused
        if entryData[0] == 0xFF:
            continue
        # build the list of occupied blocks
        firstBlock = entryData[13]
        blockchain = [firstBlock]
        currentBlock = firstBlock
        while bat[currentBlock].hasNext:
            currentBlock = bat[bat[currentBlock].status]
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
                TypeOfFile.fromInt(entryData[11]),
                TypeOfData.fromInt(entryData[12]),
                firstBlock,
                blockchain,
                entry[14] * 256 + entry[15],
            )
        ]
    return result


def extractCatalogFromTrack(
    data: bytearray or bytes, typeOfDiskImage: TypeOfDiskImage = EMULATOR_FLOPPY_IMAGE
):
    intervalOfSlice = typeOfDiskImage.sizeOfSector()
    # extract BAT
    bat = extractBlockAllocationTableFromSector(
        data[intervalOfSlice : intervalOfSlice + 256]
    )

    # extract catalog entries.
    catalog = []
    for i in range(2, 16):
        startOfSector = i * intervalOfSlice
        catalog += extractCatalogEntriesFromSector(
            data[startOfSector : startOfSector + 256], bat
        )

    return (bat, catalog)


######################################################## BEGIN HERE


class DiskSector:
    ###
    # We will work either with Double Density sectors, or SDDrive sectors
    #
    SIZE_OF_SECTOR_DD = 256  # we will work with double density image
    SIZE_OF_SECTOR_SDDRIVE = (
        512  # original sector filled with padding value to match SD Card sector size
    )
    FILLER_FDDRIVE = 0xE5  # seems to be the value written by a floppy drive when low-level formatting.

    ###
    # SDDrive sectors are just normal sectors embedded in a SD Card sector.
    #
    FILLER_SDDRIVE = 0xFF  # used to fill spacing data
    SDDRIVE_PADDING_DD = bytes(
        [FILLER_SDDRIVE for i in range(SIZE_OF_SECTOR_SDDRIVE - SIZE_OF_SECTOR_DD)]
    )  # padding to add after sector data

    ###
    # For the day there is to manage Simple Density sectors
    #
    # SIZE_OF_SECTOR_SD = 128
    # SDDRIVE_PADDING_SD = bytes([FILLER_SDDRIVE for i in range (SIZE_OF_SECTOR_SDDRIVE - SIZE_OF_SECTOR_SD)])

    @staticmethod
    def sizeOfSector(typeOfDiskImage: TypeOfDiskImage):
        return (
            SIZE_OF_SECTOR_DD
            if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE
            else SIZE_OF_SECTOR_SDDRIVE
        )

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        # always use self._sizeOfPayload for the day there is simple density.
        self._sizeOfPayload = SIZE_OF_SECTOR_DD
        self._typeOfDiskImage = typeOfDiskImage
        self._sizeOfSector = DiskSector.sizeOfSector(typeOfDiskImage)

        if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE:
            self._padding = None
        else:
            self._padding = SDDRIVE_PADDING_DD

        # Only takes care of the floppy sector, without filling data for sddrive.
        if len(rawData) < self._sizeOfPayload:
            self._data = bytearray([FILLER_FDDRIVE for i in range(self._sizeOfPayload)])
            self._data[: len(rawData)] = rawData
        else:
            self._data = bytearray(rawData[: self._sizeOfPayload])

    @property
    def data(self) -> bytes:
        return (
            bytes(self._data)
            if self.typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE
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
        self._data[:] = bytearray([FILLER_FDDRIVE for i in range(self._sizeOfPayload)])


class DiskTrack:
    SECTORS_PER_TRACK = 16

    @staticmethod
    def sizeOfTrack(sizeOfSector: int):
        return SECTORS_PER_TRACK * sizeOfSector

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        self._sizeOfSector = _sizeOfSector = DiskSector.sizeOfSector(typeOfDiskImage)
        self._sizeOfTrack = _sizeOfTrack = DiskTrack.sizeOfTrack(_sizeOfSector)
        dataSize = len(rawData)

        if dataSize == 0:
            self._sectors = [
                DiskSector(typeOfDiskImage=typeOfDiskImage)
                for i in range(SECTORS_PER_TRACK)
            ]
        elif dataSize >= _sizeOfTrack:
            self._sectors = [
                DiskSector(
                    rawData[(i * _sizeOfSector) : ((i + 1) * _sizeOfSector)]
                    for i in range(SECTORS_PER_TRACK)
                )
            ]
        else:
            raise ValueError(
                f"Non empty rawData should have a length of {_sizeOfTrack} bytes for {typeOfDiskImage.name}, got {dataSize}"
            )

    @property
    def sectors(self):
        return [self._sectors[i] for i in range(SECTORS_PER_TRACK)]

    def write(self, rawData: bytearray or bytes):
        dataSize = len(rawData)
        if dataSize < self._sizeOfTrack:
            raise ValueError(
                f"rawData should have a length of {self._sizeOfTrack} bytes for {typeOfDiskImage.name}, got {dataSize}"
            )

        for sector in self._sectors:
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
    TRACKS_PER_SIDE = 40

    @staticmethod
    def sizeOfSide(sizeOfTrack: int):
        return TRACKS_PER_SIDE * sizeOfTrack

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
                for i in range(TRACKS_PER_SIDE)
            ]
        elif dataSize >= _sizeOfSide:
            self._tracks = [
                DiskSector(rawData[i * _sizeOfTrack : (i + 1) * _sizeOfTrack])
                for i in range(TRACKS_PER_SIDE)
            ]
        else:
            raise ValueError(
                f"Non empty rawData should have a length of {_sizeOfSide} bytes for {typeOfDiskImage.name}, got {dataSize}"
            )

    @property
    def tracks(self):
        return [self._tracks[i] for i in range(TRACKS_PER_SIDE)]
