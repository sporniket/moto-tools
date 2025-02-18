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
from moto_lib.fs_disk.catalog import CatalogEntry, CatalogEntryStatus

from .utils_disk import ImageUtils, BlockAllocationTableBuilder


def test_FileSystemController_initFileSystem_should_prepare_bat_and_catalog():
    # prepare
    imageUtils = ImageUtils(TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    imageData = imageUtils.reserveMutable()
    image = DiskSide(imageData, TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    controller = FileSystemController(image)

    # execute
    controller.initFileSystem()

    # verify
    # -- usage
    usage = controller.computeUsage()
    assert usage.reserved == 3
    assert usage.used == 0
    assert usage.free == 157
    reserved_blocks_indexes = [1, 41, 42]
    out_of_bat = [0] + list(range(161, 256))
    for i in range(256):
        assert image.tracks[20].sectors[1].dataOfPayload[i] == (
            0 if i in out_of_bat else 0xFE if i in reserved_blocks_indexes else 0xFF
        )

    # -- catalog
    catalog = controller.listFiles(
        excludeDeletedEntries=False, excludeNeverUsedEntries=False
    )
    assert len(catalog) == 112
    for i, e in enumerate(catalog):
        assert e.status == CatalogEntryStatus.NEVER_USED
