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
from moto_lib.fs_disk.catalog import CatalogEntry, TypeOfDiskFile, TypeOfData

from .utils_disk import ImageUtils, BlockAllocationTableBuilder


### Utils to prepare image content
def prepareBlockAllocationTable():
    batBuilder = BlockAllocationTableBuilder()

    # reserve block 0 to 3
    for i in range(4):
        batBuilder.withBlock(i, 0xFE)
    # blocks i in range(1,9) are last blocks with i sectors occupied
    batBuilder.withSequenceOfBlocks([5, 6, 7, 8], 1)
    return batBuilder.build()


def prepareBlockAllocationTable_full():
    batBuilder = BlockAllocationTableBuilder()

    # reserve all the blocks
    for i in range(160):
        batBuilder.withBlock(i, 0xFE)
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
    image[catItem : catItem + 32] = prepareCatalogEntry(f"A", "B", 1, 0, 8, 10)
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry(f"B", "B", 1, 0, 8, 10)
    image[catItem] = 0  # delete entry B
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry(f"C", "B", 1, 0, 7, 10)
    catItem = catItem + 32
    image[catItem : catItem + 32] = prepareCatalogEntry(f"D", "B", 1, 0, 5, 10)
    catItem = catItem + 32
    # Done preparing raw data
    return DiskSide(image, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)


def prepareDummyDiskSideWithFullBat():
    imageUtils = ImageUtils(TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    # Start preparing data
    image = imageUtils.reserveMutable()
    # Prepare BAT
    startOfBat = imageUtils.startOfSector(0, 20, 1)
    bat = prepareBlockAllocationTable_full()
    image[startOfBat : startOfBat + len(bat)] = bat
    # Prepare Catalog
    clearData = bytes([0xFF for i in range(256)])
    for s in range(2, 16):
        start = imageUtils.startOfSector(0, 20, s)
        image[start : start + 256] = clearData
    # Done preparing raw data
    return DiskSide(image, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)


def prepareDummyDiskSideWithFullCatalog():
    imageUtils = ImageUtils(TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    # Start preparing data
    image = imageUtils.reserveMutable()
    # Prepare BAT
    startOfBat = imageUtils.startOfSector(0, 20, 1)
    bat = prepareBlockAllocationTable()
    image[startOfBat : startOfBat + len(bat)] = bat
    # Prepare Full Catalog
    clearData = bytearray([0xFF for i in range(256)])
    for e in range(0, 256, 32):
        clearData[e : e + 32] = prepareCatalogEntry(f"D", "B", 1, 0, 5, 10)
    for s in range(2, 16):
        start = imageUtils.startOfSector(0, 20, s)
        image[start : start + 256] = clearData
    # Done preparing raw data
    return DiskSide(image, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)


def test_FileSystemController_writeFile_should_put_file_data_and_create_entry():
    # prepare
    diskSide = prepareDummyDiskSide()
    fs = FileSystemController(diskSide)

    # -- verify expectations on the prepared image.
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 6
    assert fsUsage.used == 4
    assert fsUsage.free == 150

    data = bytearray(255 * 18)
    for i in range(18):
        index = i * 18
        data[index : index + 255] = [i] + list(range(1, 255))

    # execute and verify 1
    fs.writeFile(data[:2295], "f1", "bas", typeOfFile=TypeOfDiskFile.BASIC_PROGRAM)

    # -- verify usage
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 6
    assert fsUsage.used == 6
    assert fsUsage.free == 148

    # -- verify BAT
    bat = diskSide.tracks[20].sectors[1].dataOfPayload[1:161]
    assert bat[4] == 9
    assert bat[9] == 0xC1

    # -- verify catalog
    entry = fs.listFiles()[1]
    assert entry.toBytes() == bytes(
        "F1      BAS".encode("ascii")
        + bytes([0, 0, 4, 0, 255] + [0xFF for i in range(16)])
    )

    # -- verify content
    fileData = fs.readFile(entry)
    assert len(fileData) == 2295
    assert fileData == data[:2295]

    # execute and verify 2
    fs.writeFile(
        data[2295:],
        "F2",
        "TXT",
        typeOfFile=TypeOfDiskFile.TEXT_FILE,
        typeOfData=TypeOfData.ASCII_DATA,
    )

    # -- verify usage
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 6
    assert fsUsage.used == 8
    assert fsUsage.free == 146

    # -- verify BAT
    bat = diskSide.tracks[20].sectors[1].dataOfPayload[1:161]
    assert bat[10] == 11
    assert bat[11] == 0xC1

    # -- verify catalog
    entry = fs.listFiles()[4]
    assert entry.toBytes() == bytes(
        "F2      TXT".encode("ascii")
        + bytes([3, 0xFF, 10, 0, 255] + [0xFF for i in range(16)])
    )

    # -- verify content
    fileData = fs.readFile(entry)
    assert len(fileData) == 2295
    assert fileData == data[2295:]


def test_FileSystemController_writeFile_cannot_write_when_bat_is_full():
    # prepare
    diskSide = prepareDummyDiskSideWithFullBat()
    fs = FileSystemController(diskSide)

    # -- verify expectations on the prepared image.
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 160
    assert fsUsage.used == 0
    assert fsUsage.free == 0

    # -- verify expectation on the catalog
    catalog = fs.listFiles()
    assert len(catalog) == 0

    data = bytearray([1])

    # execute and verify 1
    with pytest.raises(ValueError) as error:
        fs.writeFile(data[:2295], "f1", "bas", typeOfFile=TypeOfDiskFile.BASIC_PROGRAM)
    assert "not.enough.blocks:require.1:got.0" in str(error.value)

    # -- verify catalog has no new entry
    catalog = fs.listFiles()
    assert len(catalog) == 0


def test_FileSystemController_writeFile_cannot_write_when_catalog_is_full():
    # prepare
    diskSide = prepareDummyDiskSideWithFullCatalog()
    fs = FileSystemController(diskSide)

    # -- verify expectations on the prepared image.
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 6
    assert fsUsage.used == 4
    assert fsUsage.free == 150

    # -- verify expectation on the catalog
    catalog = fs.listFiles()
    assert len(catalog) == 112

    data = bytearray([1])

    # execute and verify 1
    with pytest.raises(ValueError) as error:
        fs.writeFile(data[:2295], "f1", "bas", typeOfFile=TypeOfDiskFile.BASIC_PROGRAM)
    assert "no.more.space.in.catalog" in str(error.value)

    # -- verify BAT usage has not been modified.
    fsUsage = fs.computeUsage()
    assert fsUsage.reserved == 6
    assert fsUsage.used == 4
    assert fsUsage.free == 150
