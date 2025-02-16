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

from .utils_disk import ImageUtils, BlockAllocationTableBuilder


### Utils to prepare image content
def prepareBlockAllocationTable():
    batBuilder = BlockAllocationTableBuilder()
    # blocks i in range(2,10) are last blocks with i-1 sectors occupied
    for i in range(1, 9):
        batBuilder.withBlock(i, 0xC0 + i)
    # block 10 points to block 2 to make a 2-blocks files
    batBuilder.withBlock(9, 1)
    return batBuilder.build()


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
    startOfDataSector = imageUtils.startOfSector(0, 0, 8)
    for i in range(72):
        image[startOfDataSector : startOfDataSector + 256] = [i] + list(range(1, 255))
        startOfDataSector = (
            startOfDataSector + TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE.sizeOfSector()
        )
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
    for n, i in enumerate(range(1, 10)):
        image[catItem : catItem + 32] = prepareCatalogEntry(f"C{i}", "A", 1, 0, i, 255)
        catItem = catItem + 32
        if (n + 1) % 8 == 0:
            # Accomodate SDDrive image structure
            catItem = catItem + 256
    # Done preparing raw data
    return DiskSide(image, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)


def test_FileSystemController_readFile_should_extract_file_data():
    fs = FileSystemController(prepareDummyDiskSide())
    for index, entry in enumerate(fs.listFiles()):
        i = index + 1  # expected i for "c{i}.a"
        entryData = entry.toDict()
        # basic check on the name
        assert f"C{i}" == entryData["name"].rstrip()
        fileData = fs.readFile(entry)
        # actual check on the data
        assert len(fileData) == entryData["sizeInBytes"]
        for chunck in range(i):
            expectedData = (
                bytes([8 * index + chunck] + list(range(1, 255)))
                if chunck < 8
                else bytes([chunck - 8] + list(range(1, 255)))
            )
            assert fileData[chunck * 255 : (chunck + 1) * 255] == expectedData
