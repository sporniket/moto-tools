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
from moto_lib.fs_disk.image import DiskSide, DiskSector


def copyBytes(fromBytes, toBytes, toStart):
    _cursor = toStart
    for b in fromBytes:
        toBytes[_cursor] = b
        _cursor = _cursor + 1


def prepareBlocAllocationTable(target, index):
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
    copyBytes(bat, target, index)


def prepareCatalogEntry(
    catalog: bytearray,
    index: int,
    name: str,
    extension: str,
    type: int,
    dataType: int,
    firstBlock: int,
    lastSectorUsage: int,
):
    cursor = index * 32
    _name = name.upper() + "        "
    for c in _name[:8]:
        catalog[cursor] = c & 0xFF
        cursor = cursor + 1
    _extension = extension.upper() + "   "
    for c in _extension[:3]:
        catalog[cursor] = c & 0xFF
        cursor = cursor + 1
    data = bytearray(
        [
            type,
            dataType,
            firstBlock,
            (lastSectorUsage >> 8) & 0xFF,
            lastSectorUsage & 0xFF,
        ]
    )
    for d in data:
        catalog[cursor] = d
        cursor = cursor + 1


def prepareCatalogEntry__deleted(
    catalog: bytearray,
    index: int,
    name: str,
    extension: str,
    type: int,
    dataType: int,
    firstBlock: int,
    lastSectorUsage: int,
):
    cursor = index * 32
    _name = name.upper() + "        "
    catalog[cursor] = 0
    cursor = cursor + 1
    for c in _name[1:8]:
        catalog[cursor] = c & 0xFF
        cursor = cursor + 1
    _extension = extension.upper() + "   "
    for c in _extension[:3]:
        catalog[cursor] = c & 0xFF
        cursor = cursor + 1
    data = bytearray(
        [
            type,
            dataType,
            firstBlock,
            (lastSectorUsage >> 8) & 0xFF,
            lastSectorUsage & 0xFF,
        ]
    )
    for d in data:
        catalog[cursor] = d
        cursor = cursor + 1


def prepareTrack20():
    sector1 = DiskSector()
    sector2 = DiskSector(prepareBlocAllocationTable)


def prepareDummyDiskSide():
    return DiskSide(bytes())


def test_FileSystemController_computeUsage__should_compute_usage():
    usage = FileSystemController(prepareDummyDiskSide()).computeUsage()

    assert usage.used == 13
    assert usage.reserved == 1
    assert usage.free == 146


def test_FileSystemController_listFiles__should_list_catalog_entries():
    fs = FileSystemController(prepareDummyDiskSide())

    # default list
    entries = fs.listFiles()
    assert len(entries) == 4

    entries = fs.listFiles(excludeDeletedEntries=False)
    assert len(entries) == 5

    entries = fs.listFiles(excludeFreeEntries=False)
    assert len(entries) == 111

    entries = fs.listFiles(excludeDeletedEntries=False, excludeFreeEntries=False)
    assert len(entries) == 112
