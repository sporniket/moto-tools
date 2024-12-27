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

import pytest

from moto_lib.fs_disk.controller import FileSystemController
from moto_lib.fs_disk.image import TypeOfDiskImage, DiskSide, DiskSector
from moto_lib.fs_disk.catalog import CatalogEntry


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


### Utils to prepare image content
def prepareBlockAllocationTable():
    bat = bytearray([0xFF for i in range(256)])
    # reserve block 0 (boot sector), 40 and 41 (track 20 hosting the bat and catalog)
    for i in [0, 40, 41]:
        bat[i] = 0xFE
    # blocks 2->3->5, 3 sectors used on block 5
    bat[2] = 3
    bat[3] = 5
    bat[5] = 195
    # block 4, 1 sector used
    bat[4] = 193
    # blocks 6->7, 8 sectors used on block 7
    bat[6] = 7
    bat[7] = 200
    # blocks 8->9->10->11->12->13->14, 3 sectors used on block 14
    bat[8] = 9
    bat[9] = 10
    bat[10] = 11
    bat[11] = 12
    bat[12] = 13
    bat[13] = 14
    bat[14] = 195
    return bat


def prepareCatalogEntry(
    name: str,
    extension: str,
    type: int,
    dataType: int,
    firstBlock: int,
    lastSectorUsage: int,
):
    entry = bytearray([0xFF for i in range(32)])
    cursor = 0
    _name = name.upper() + "        "
    for c in _name[:8]:
        entry[cursor] = ord(c) & 0xFF
        cursor = cursor + 1
    _extension = extension.upper() + "   "
    for c in _extension[:3]:
        entry[cursor] = ord(c) & 0xFF
        cursor = cursor + 1
    entry[11:16] = bytearray(
        [
            type,
            dataType,
            firstBlock,
            (lastSectorUsage >> 8) & 0xFF,
            lastSectorUsage & 0xFF,
        ]
    )
    return entry


def prepareDummyDiskSide():
    imageUtils = ImageUtils(TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    # Start preparing data
    image = imageUtils.reserveMutable()
    # Prepare BAT
    startOfBat = imageUtils.startOfSector(0, 20, 1)
    bat = prepareBlockAllocationTable()
    image[startOfBat : startOfBat + len(bat)] = bat
    # Prepare Catalog
    clearData = bytes([0xFF for i in range(256)])
    for s in range(2, 16):
        start = imageUtils.startOfSector(0, 20, s)
        image[start : start + 256] = clearData
    catItem = imageUtils.startOfSector(0, 20, 2)
    image[catItem : catItem + 32] = prepareCatalogEntry(
        "A", "B", 0, 0, 2, 10
    )  # 10 = 4600 - 255 * 18
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry("B", "B", 0, 0, 1, 10)
    image[catItem] = 0  # delete entry
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry("C", "B", 1, 0, 4, 130)
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry(
        "D", "B", 2, 0, 6, 175
    )  # 175 = 4000 - 255 * 15
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry(
        "E", "TXT", 3, 0xFF, 8, 250
    )  # 150 = 13000 - 255 * 50
    # Done preparing raw data
    return DiskSide(image, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)


def test_FileSystemController_computeUsage__should_compute_usage():
    usage = FileSystemController(prepareDummyDiskSide()).computeUsage()

    assert usage.used == 13
    assert usage.reserved == 3
    assert usage.free == 144


def test_FileSystemController_listFiles__should_list_catalog_entries():
    fs = FileSystemController(prepareDummyDiskSide())

    # default list
    entries = fs.listFiles()
    assert len(entries) == 4
    assert entries[0].toDict() == {
        "status": "ALIVE",
        "name": "A       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 3,
        "sizeInBytes": 4600,
    }
    assert entries[1].toDict() == {
        "status": "ALIVE",
        "name": "C       ",
        "extension": "B  ",
        "typeOfFile": "DATA",
        "typeOfData": "BINARY",
        "sizeInBlocks": 1,
        "sizeInBytes": 130,
    }
    assert entries[2].toDict() == {
        "status": "ALIVE",
        "name": "D       ",
        "extension": "B  ",
        "typeOfFile": "MODULE",
        "typeOfData": "BINARY",
        "sizeInBlocks": 2,
        "sizeInBytes": 4000,
    }
    assert entries[3].toDict() == {
        "status": "ALIVE",
        "name": "E       ",
        "extension": "TXT",
        "typeOfFile": "TEXT",
        "typeOfData": "ASCII",
        "sizeInBlocks": 7,
        "sizeInBytes": 13000,
    }

    entries = fs.listFiles(excludeDeletedEntries=False)
    assert len(entries) == 5
    assert entries[0].toDict() == {
        "status": "ALIVE",
        "name": "A       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 3,
        "sizeInBytes": 4600,
    }
    assert entries[1].toDict() == {
        "status": "DELETED",
        "name": "x       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 0,
        "sizeInBytes": 0,
    }
    assert entries[2].toDict() == {
        "status": "ALIVE",
        "name": "C       ",
        "extension": "B  ",
        "typeOfFile": "DATA",
        "typeOfData": "BINARY",
        "sizeInBlocks": 1,
        "sizeInBytes": 130,
    }
    assert entries[3].toDict() == {
        "status": "ALIVE",
        "name": "D       ",
        "extension": "B  ",
        "typeOfFile": "MODULE",
        "typeOfData": "BINARY",
        "sizeInBlocks": 2,
        "sizeInBytes": 4000,
    }
    assert entries[4].toDict() == {
        "status": "ALIVE",
        "name": "E       ",
        "extension": "TXT",
        "typeOfFile": "TEXT",
        "typeOfData": "ASCII",
        "sizeInBlocks": 7,
        "sizeInBytes": 13000,
    }

    entries = fs.listFiles(excludeNeverUsedEntries=False)
    assert len(entries) == 111
    assert entries[0].toDict() == {
        "status": "ALIVE",
        "name": "A       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 3,
        "sizeInBytes": 4600,
    }
    assert entries[1].toDict() == {
        "status": "ALIVE",
        "name": "C       ",
        "extension": "B  ",
        "typeOfFile": "DATA",
        "typeOfData": "BINARY",
        "sizeInBlocks": 1,
        "sizeInBytes": 130,
    }
    assert entries[2].toDict() == {
        "status": "ALIVE",
        "name": "D       ",
        "extension": "B  ",
        "typeOfFile": "MODULE",
        "typeOfData": "BINARY",
        "sizeInBlocks": 2,
        "sizeInBytes": 4000,
    }
    assert entries[3].toDict() == {
        "status": "ALIVE",
        "name": "E       ",
        "extension": "TXT",
        "typeOfFile": "TEXT",
        "typeOfData": "ASCII",
        "sizeInBlocks": 7,
        "sizeInBytes": 13000,
    }
    for e in entries[4:]:
        assert e.toDict() == {"status": "NEVER_USED"}

    entries = fs.listFiles(excludeDeletedEntries=False, excludeNeverUsedEntries=False)
    assert len(entries) == 112
    assert entries[0].toDict() == {
        "status": "ALIVE",
        "name": "A       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 3,
        "sizeInBytes": 4600,
    }
    assert entries[1].toDict() == {
        "status": "DELETED",
        "name": "x       ",
        "extension": "B  ",
        "typeOfFile": "BASIC",
        "typeOfData": "TOKEN",
        "sizeInBlocks": 0,
        "sizeInBytes": 0,
    }
    assert entries[2].toDict() == {
        "status": "ALIVE",
        "name": "C       ",
        "extension": "B  ",
        "typeOfFile": "DATA",
        "typeOfData": "BINARY",
        "sizeInBlocks": 1,
        "sizeInBytes": 130,
    }
    assert entries[3].toDict() == {
        "status": "ALIVE",
        "name": "D       ",
        "extension": "B  ",
        "typeOfFile": "MODULE",
        "typeOfData": "BINARY",
        "sizeInBlocks": 2,
        "sizeInBytes": 4000,
    }
    assert entries[4].toDict() == {
        "status": "ALIVE",
        "name": "E       ",
        "extension": "TXT",
        "typeOfFile": "TEXT",
        "typeOfData": "ASCII",
        "sizeInBlocks": 7,
        "sizeInBytes": 13000,
    }
    for e in entries[5:]:
        assert e.toDict() == {"status": "NEVER_USED"}
