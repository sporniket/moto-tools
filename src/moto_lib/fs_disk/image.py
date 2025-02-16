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

    def sizeOfPayload(self):
        return 256


######################################################## BEGIN HERE
# private shorthand values
_SIZE_OF_SECTOR_DD = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE.sizeOfSector()
_SIZE_OF_SECTOR_SDDRIVE = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE.sizeOfSector()
_FILLER_PAYLOAD = (
    0xE5  # seems to be the value written by a floppy drive when low-level formatting.
)
_FILLER_SDDRIVE = 0xFF

#### =====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====---=====
## Extraction des données disques


class DiskSector:
    ###
    # We will work either with Double Density sectors, or SDDrive sectors
    #
    SIZE_OF_SECTOR_DD = _SIZE_OF_SECTOR_DD  # we will work with double density image
    SIZE_OF_SECTOR_SDDRIVE = _SIZE_OF_SECTOR_SDDRIVE  # original sector filled with padding value to match SD Card sector size
    SDDRIVE_PADDING_DD = bytes(
        [
            _FILLER_SDDRIVE
            for i in range(
                TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE.sizeOfSector()
                - TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE.sizeOfPayload()
            )
        ]
    )  # padding to add after sector data

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        # always use self._sizeOfPayload for the day there is simple density.
        self._typeOfDiskImage = typeOfDiskImage
        self._data = bytearray(typeOfDiskImage.sizeOfSector())

        if typeOfDiskImage == TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE:
            self._data[
                typeOfDiskImage.sizeOfPayload() : typeOfDiskImage.sizeOfSector()
            ] = DiskSector.SDDRIVE_PADDING_DD

        # Only takes care of the floppy sector, without filling data for sddrive.
        sizeOfRawData = len(rawData)
        if sizeOfRawData == 0:
            self._data[0 : typeOfDiskImage.sizeOfPayload()] = [
                _FILLER_PAYLOAD for i in range(typeOfDiskImage.sizeOfPayload())
            ]
        elif sizeOfRawData >= typeOfDiskImage.sizeOfSector():
            self._data[0 : typeOfDiskImage.sizeOfPayload()] = rawData[
                0 : typeOfDiskImage.sizeOfPayload()
            ]
        else:
            raise ValueError(
                f"Must provide a byte array of {typeOfDiskImage.sizeOfSector()}, got {len(rawData)}"
            )

    @property
    def dataOfSector(self) -> bytes:
        return bytes(self._data)

    @property
    def dataOfPayload(self) -> bytes:
        return bytes(self._data[0 : self._typeOfDiskImage.sizeOfPayload()])

    @dataOfPayload.setter
    def dataOfPayload(self, value: bytearray or bytes):
        copyLen = len(value)
        copyLen = (
            copyLen
            if copyLen < self._typeOfDiskImage.sizeOfPayload()
            else self._typeOfDiskImage.sizeOfPayload()
        )
        self._data[0:copyLen] = value


class DiskTrack:
    SECTORS_PER_TRACK = 16

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        _sizeOfSector = typeOfDiskImage.sizeOfSector()
        self._sizeOfTrack = _sizeOfTrack = _sizeOfSector * DiskTrack.SECTORS_PER_TRACK
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


class DiskSide:
    # expected size of a side depending of the type of disk image
    SIZE_OF_SIDE = [327680, 655360]
    TRACKS_PER_SIDE = 80

    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        _sizeOfTrack = typeOfDiskImage.sizeOfSector() * DiskTrack.SECTORS_PER_TRACK
        self._sizeOfSide = _sizeOfSide = _sizeOfTrack * DiskSide.TRACKS_PER_SIDE
        self._typeOfDiskImage = typeOfDiskImage
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

    @property
    def tracks(self):
        return [self._tracks[i] for i in range(DiskSide.TRACKS_PER_SIDE)]


class DiskImage:
    def __init__(
        self,
        rawData: bytearray or bytes = bytes(),
        *,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
        wantedNumberOfSides: int = 4,
    ):
        SIZE_OF_SIDE = (
            327680
            if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE
            else 655360
        )

        # * whether it is an emulator or sddrive image
        #   * check length validity (emulator : integer multiple of base size ; sddrive : fixed size)
        #   * assess number of side (emulator : 2 or 4 ; sddrive : 4 )
        #   * instanciate each disk sides
        self._sides = sides = []  # TODO
        dataSize = len(rawData)
        actualData = rawData
        numberOfSides = 0

        if dataSize == 0:
            if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE:
                numberOfSides = wantedNumberOfSides if wantedNumberOfSides <= 4 else 4
                if wantedNumberOfSides == 3:
                    raise ValueError(
                        f"Emulator disk images MUST be created with 1, 2 or 4 sides, got {wantedNumberOfSides}"
                    )
                self._sides = [
                    DiskSide(typeOfDiskImage=typeOfDiskImage)
                    for i in range(numberOfSides)
                ]
            else:  # typeOfDiskImage == TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE:
                # sddrive image always have 4 sides
                self._sides = [
                    DiskSide(typeOfDiskImage=typeOfDiskImage) for i in range(4)
                ]

        else:
            numberOfSides = min([dataSize // SIZE_OF_SIDE, 4])
            if typeOfDiskImage == TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE:
                if numberOfSides in [0, 3]:
                    raise ValueError(
                        f"Emulator disk images MUST embed 1, 2 or 4 disk sides, got {numberOfSides}."
                    )
            else:  # typeOfDiskImage == TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE:
                if numberOfSides < 4:
                    raise ValueError(
                        f"SDDrive images MUST embed 4 disk sides, got {numberOfSides}."
                    )

            if numberOfSides < 4 and numberOfSides * SIZE_OF_SIDE < dataSize:
                raise ValueError(
                    f"Disk image MUST contains an integral number of sides, {dataSize} is not enough for {numberOfSides + 1} sides."
                )

            self._sides = [
                DiskSide(
                    rawData[i * SIZE_OF_SIDE : (i + 1) * SIZE_OF_SIDE],
                    typeOfDiskImage=typeOfDiskImage,
                )
                for i in range(numberOfSides)
            ]

    @property
    def sides(self) -> List[DiskSide]:
        return [self._sides[i] for i in range(len(self._sides))]
