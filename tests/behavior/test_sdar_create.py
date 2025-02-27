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
FILE_G = "g.dat"

FILE_LONG_NAME = "too_long_name.foo"
FILE_LONG_EXTENSION = "too_long.extension"
FILE_NOT_FOUND = "whatever.foo"

COMMON_FILESET = [
    FILE_A,
    FILE_B,
    FILE_C,
    FILE_D,
    FILE_E,
]

REJECTED_FILESET = [FILE_LONG_NAME, FILE_LONG_EXTENSION]


# File name of created archive
FILE_IMAGE = "result.sd"


def prepareBigFileContent(size: int) -> bytes:
    result = bytearray(size)
    oneBlock = bytearray(i for j in list(range(8)) for i in list(range(255)))
    blockSize = len(oneBlock)

    # self verify
    assert blockSize == 255 * 8
    oneChunk = bytes([i for i in range(255)])
    for j in range(8):
        assert oneBlock[j * 255] == 0 and oneBlock[j * 255 : (j + 1) * 255] == oneChunk

    # proceeds
    fullBlocks, remainder = size // blockSize, size % blockSize
    start = 0
    for i in range(fullBlocks):
        oneBlock[0] = i & 0xFF
        result[start : start + blockSize] = oneBlock
        start = start + blockSize
    if remainder > 0:
        oneBlock[0] = fullBlocks & 0xFF
        result[start:] = oneBlock[:remainder]
    return bytes(result)


def test_that_it_does_create_image_file():
    sourceFileSet = COMMON_FILESET + REJECTED_FILESET
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in sourceFileSet]
    )
    createdImageFile = os.path.join(tmp_dir, FILE_IMAGE)
    baseArgs = ["prog", "--create", createdImageFile]
    sourceArgs = sourceFileSet + [FILE_NOT_FOUND]
    sourceArgs[1] = sourceArgs[1] + ",a"
    with patch.object(
        sys, "argv", baseArgs + [os.path.join(tmp_dir, f) for f in sourceArgs]
    ):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == f"""Side 0
  A.BAS...ok
  B.BAS...ok
  C.FOO...ok
  D.TXT...ok
  E.BIN...ok
  -- too long name : {tmp_dir}/too_long_name.foo
  -- too long extension : {tmp_dir}/too_long.extension
  -- not found : {tmp_dir}/whatever.foo
5 files
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
5 files
"""
        )

        # Verify archive file
        assert os.path.exists(createdImageFile)
        # -- load the binary file as DiskImage
        with open(createdImageFile, mode="rb") as infile:
            actualImageData = infile.read()
        actualImage = DiskImage(
            actualImageData, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        )
        # -- verify side 0
        fs = FileSystemController(actualImage.sides[0])
        usage = fs.computeUsage()
        assert usage.used == 5
        assert usage.reserved == 3
        assert usage.free == 152
        # -- -- get catalog and verify
        catalog = fs.listFiles()
        assert len(catalog) == 5
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "BAS",
                "name": "A       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "TOKEN",
                "typeOfFile": "BASIC",
            },
            {
                "extension": "BAS",
                "name": "B       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "BASIC",
            },
            {
                "extension": "FOO",
                "name": "C       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "DATA",
            },
            {
                "extension": "TXT",
                "name": "D       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "TEXT",
            },
            {
                "extension": "BIN",
                "name": "E       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "MODULE",
            },
        ]
        assert [fs.readFile(f) for f in catalog] == [
            d
            for d in [
                "aaaaaaaaaa\n".encode(encoding="ascii"),
                "bbbbbbbbbb\n".encode(encoding="ascii"),
                "cccccccccc\n".encode(encoding="ascii"),
                "dddddddddd\n".encode(encoding="ascii"),
                "eeeeeeeeee\n".encode(encoding="ascii"),
            ]
        ]
        # -- verify side 1
        fs = FileSystemController(actualImage.sides[1])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0
        # -- verify side 2
        fs = FileSystemController(actualImage.sides[2])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0
        # -- verify side 3
        fs = FileSystemController(actualImage.sides[3])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0


def test_that_it_goes_to_the_next_disk_side_with_eos_switch():
    sourceFileSet = COMMON_FILESET
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in sourceFileSet]
    )
    createdImageFile = os.path.join(tmp_dir, FILE_IMAGE)
    baseArgs = ["prog", "--create", createdImageFile]
    sourceArgs = [os.path.join(tmp_dir, f) for f in sourceFileSet]
    sourceArgs[1] = sourceArgs[1] + ",a"
    sourceArgs = (
        sourceArgs[0:2]
        + ["--eos"]
        + sourceArgs[2:3]
        + ["--eos", "--eos"]
        + sourceArgs[3:]
    )
    with patch.object(sys, "argv", baseArgs + ["--"] + sourceArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == f"""Side 0
  A.BAS...ok
  B.BAS...ok
2 files
---
Side 1
  C.FOO...ok
1 file
---
Side 2
0 files
---
Side 3
  D.TXT...ok
  E.BIN...ok
2 files
---
TOTAL
5 files
"""
        )

        # Verify archive file
        assert os.path.exists(createdImageFile)
        # -- load the binary file as DiskImage
        with open(createdImageFile, mode="rb") as infile:
            actualImageData = infile.read()
        actualImage = DiskImage(
            actualImageData, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        )
        # -- verify side 0
        fs = FileSystemController(actualImage.sides[0])
        usage = fs.computeUsage()
        assert usage.used == 2
        assert usage.reserved == 3
        assert usage.free == 155
        # -- -- get catalog and verify
        catalog = fs.listFiles()
        assert len(catalog) == 2
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "BAS",
                "name": "A       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "TOKEN",
                "typeOfFile": "BASIC",
            },
            {
                "extension": "BAS",
                "name": "B       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "BASIC",
            },
        ]
        assert [fs.readFile(f) for f in catalog] == [
            d
            for d in [
                "aaaaaaaaaa\n".encode(encoding="ascii"),
                "bbbbbbbbbb\n".encode(encoding="ascii"),
            ]
        ]
        # -- verify side 1
        fs = FileSystemController(actualImage.sides[1])
        usage = fs.computeUsage()
        assert usage.used == 1
        assert usage.reserved == 3
        assert usage.free == 156
        # -- -- get catalog and verify
        catalog = fs.listFiles()
        assert len(catalog) == 1
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "FOO",
                "name": "C       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "DATA",
            },
        ]
        assert [fs.readFile(f) for f in catalog] == [
            d
            for d in [
                "cccccccccc\n".encode(encoding="ascii"),
            ]
        ]
        # -- verify side 2
        fs = FileSystemController(actualImage.sides[2])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0
        # -- verify side 3
        fs = FileSystemController(actualImage.sides[3])
        usage = fs.computeUsage()
        assert usage.used == 2
        assert usage.reserved == 3
        assert usage.free == 155
        # -- -- get catalog and verify
        catalog = fs.listFiles()
        assert len(catalog) == 2
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "TXT",
                "name": "D       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "TEXT",
            },
            {
                "extension": "BIN",
                "name": "E       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "MODULE",
            },
        ]
        assert [fs.readFile(f) for f in catalog] == [
            d
            for d in [
                "dddddddddd\n".encode(encoding="ascii"),
                "eeeeeeeeee\n".encode(encoding="ascii"),
            ]
        ]


def test_that_it_goes_to_the_next_disk_side_when_the_file_is_too_big_for_the_current_side():
    # prepare
    sourceFileSet = COMMON_FILESET
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in sourceFileSet]
    )

    bigFileName = os.path.join(tmp_dir, FILE_G)
    bigFileContent = prepareBigFileContent(312000)  # needs 153 blocks
    with open(bigFileName, "wb") as f:
        f.write(bigFileContent)

    # execute
    createdImageFile = os.path.join(tmp_dir, FILE_IMAGE)
    baseArgs = ["prog", "--create", createdImageFile]
    sourceArgs = [os.path.join(tmp_dir, f) for f in sourceFileSet]
    sourceArgs[1] = sourceArgs[1] + ",a"
    sourceArgs.append(bigFileName)
    with patch.object(sys, "argv", baseArgs + sourceArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == f"""Side 0
  A.BAS...ok
  B.BAS...ok
  C.FOO...ok
  D.TXT...ok
  E.BIN...ok
  G.DAT...too big
5 files
---
Side 1
  G.DAT...ok
1 file
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
            actualImageData = infile.read()
        actualImage = DiskImage(
            actualImageData, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        )
        # -- verify side 0
        fs = FileSystemController(actualImage.sides[0])
        usage = fs.computeUsage()
        assert usage.used == 5
        assert usage.reserved == 3
        assert usage.free == 152
        # -- -- get catalog and verify
        catalog = fs.listFiles()
        assert len(catalog) == 5
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "BAS",
                "name": "A       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "TOKEN",
                "typeOfFile": "BASIC",
            },
            {
                "extension": "BAS",
                "name": "B       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "BASIC",
            },
            {
                "extension": "FOO",
                "name": "C       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "DATA",
            },
            {
                "extension": "TXT",
                "name": "D       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "ASCII",
                "typeOfFile": "TEXT",
            },
            {
                "extension": "BIN",
                "name": "E       ",
                "sizeInBlocks": 1,
                "sizeInBytes": 11,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "MODULE",
            },
        ]
        assert [fs.readFile(f) for f in catalog] == [
            d
            for d in [
                "aaaaaaaaaa\n".encode(encoding="ascii"),
                "bbbbbbbbbb\n".encode(encoding="ascii"),
                "cccccccccc\n".encode(encoding="ascii"),
                "dddddddddd\n".encode(encoding="ascii"),
                "eeeeeeeeee\n".encode(encoding="ascii"),
            ]
        ]
        # -- verify side 1
        fs = FileSystemController(actualImage.sides[1])
        usage = fs.computeUsage()
        assert usage.used == 153
        assert usage.reserved == 3
        assert usage.free == 4
        catalog = fs.listFiles()
        assert len(catalog) == 1
        assert [f.toDict() for f in catalog] == [
            {
                "extension": "DAT",
                "name": "G       ",
                "sizeInBlocks": 153,
                "sizeInBytes": 312000,
                "status": "ALIVE",
                "typeOfData": "BINARY",
                "typeOfFile": "DATA",
            },
        ]
        actualContent = fs.readFile(catalog[0])
        assert actualContent == bigFileContent
        # -- verify side 2
        fs = FileSystemController(actualImage.sides[2])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0
        # -- verify side 3
        fs = FileSystemController(actualImage.sides[3])
        usage = fs.computeUsage()
        assert usage.used == 0
        assert usage.reserved == 3
        assert usage.free == 157
        assert len(fs.listFiles()) == 0


def test_that_it_discards_all_files_when_eos_switch_is_used_too_much_before():
    sourceFileSet = COMMON_FILESET
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in sourceFileSet]
    )
    createdImageFile = os.path.join(tmp_dir, FILE_IMAGE)
    baseArgs = ["prog", "--create", createdImageFile]
    sourceArgs = [os.path.join(tmp_dir, f) for f in sourceFileSet]
    sourceArgs[1] = sourceArgs[1] + ",a"
    tooMuchEoses = ["--eos", "--eos", "--eos", "--eos"]
    with patch.object(sys, "argv", baseArgs + ["--"] + tooMuchEoses + sourceArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == f"""Side 0
0 files
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
0 files
"""
        )

        # Verify archive file
        assert os.path.exists(createdImageFile)
        # -- load the binary file as DiskImage
        with open(createdImageFile, mode="rb") as infile:
            actualImageData = infile.read()
        actualImage = DiskImage(
            actualImageData, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        )
        # -- verify each side
        for s in range(4):
            fs = FileSystemController(actualImage.sides[0])
            usage = fs.computeUsage()
            assert usage.used == 0
            assert usage.reserved == 3
            assert usage.free == 157
            assert len(fs.listFiles()) == 0
