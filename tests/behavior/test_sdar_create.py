"""
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

import os
import shutil
import time
import sys
import io
from typing import List, Union, Optional

from unittest.mock import patch
from contextlib import redirect_stdout

# from moto_fdar import DiskArchiveCli
from moto_sdar import DiskArchiveCli
from moto_lib.fs_disk.image import DiskImage, DiskSide, TypeOfDiskImage
from moto_lib.fs_disk.controller import FileSystemController, FileSystemUsage

from .utils import (
    initializeTmpWorkspace,
    assert_that_source_is_converted_as_expected,
)

# Directories
source_dir = os.path.join("tests", "data", "create-disk-image")
expected_dir = os.path.join("tests", "data.expected")

# File names of source files
FILE_A = "a.bas"
FILE_B = "b.bas"
FILE_C = "c.foo"
FILE_D = "d.txt"
FILE_E = "e.bin"
FILE_F = "f.lst"
FILE_G = "g.dat"

COMMON_FILESET = [
    FILE_A,
    FILE_B,
    FILE_C,
    FILE_D,
    FILE_E,
    FILE_F,
]

# File name of created archive
FILE_IMAGE = "result.sd"


def test_that_it_does_create_image_file():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in COMMON_FILESET]
    )
    createdImageFile = os.path.join(tmp_dir, FILE_IMAGE)
    baseArgs = ["prog", "--create", "--into", tmp_dir, createdImageFile]
    sourceArgs = [
        FILE_A,
        FILE_B,
        FILE_C,
        FILE_D,
        FILE_E,
        FILE_F,
    ]
    with patch.object(sys, "argv", baseArgs + sourceArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """Side 0
  A.BAS...ok
  B.BAS...ok
  C.FOO...ok
  D.TXT...ok
  E.BIN...ok
  -- f.lst --> f.bas,a
  F.BAS...ok
6 files
---
Side 1
0 files
---
Side 2
0 files
---
Side 3
0 files
---
TOTAL
6 files
"""
        )

        # Verify archive file
        assert os.path.exists(createdImageFile)
        # -- load the binary file as DiskImage
        with open(createdImageFile, mode="rb") as infile:
            actualImageData = infile.readall()
        actualImage = DiskImage(
            actualImageData, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        )
        # -- verify side 0
        fs = FileSystemController(actualImage.sides[0])
        usage = fs.computeUsage()
        assert usage.used == 6
        assert usage.reserved == 3
        assert usage.free == 151
        # -- -- TODO verify each file in catalog, then extract and assert data size and content
        # -- verify side 1
        fs = FileSystemController(actualImage.sides[1])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        # -- verify side 2
        fs = FileSystemController(actualImage.sides[2])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        # -- verify side 3
        fs = FileSystemController(actualImage.sides[3])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
