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
from moto_lib.fs_disk.image import DiskSide


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
