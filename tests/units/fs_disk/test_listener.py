"""
---
(c) 2022~2024 David SPORN
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

import io
from contextlib import redirect_stdout

from moto_lib.fs_disk.listener import (
    DiskImageCliListenerQuiet,
    DiskImageCliListenerVerbose,
    TypeOfDiskImageProcessing,
)
from moto_lib.fs_disk.controller import FileSystemUsage

entryA = {
    "status": "ALIVE",
    "name": "A       ",
    "extension": "B  ",
    "typeOfFile": "BASIC",
    "typeOfData": "TOKEN",
    "sizeInBlocks": 3,
    "sizeInBytes": 4600,
}

entryB = {
    "status": "DELETED",
    "name": "x       ",
    "extension": "B  ",
    "typeOfFile": "BASIC",
    "typeOfData": "TOKEN",
    "sizeInBlocks": 0,
    "sizeInBytes": 0,
}

entryC = {
    "status": "ALIVE",
    "name": "C       ",
    "extension": "B  ",
    "typeOfFile": "DATA",
    "typeOfData": "BINARY",
    "sizeInBlocks": 1,
    "sizeInBytes": 130,
}

entryD = {
    "status": "ALIVE",
    "name": "D       ",
    "extension": "B  ",
    "typeOfFile": "MODULE",
    "typeOfData": "BINARY",
    "sizeInBlocks": 2,
    "sizeInBytes": 4000,
}

entryE = {
    "status": "ALIVE",
    "name": "E       ",
    "extension": "TXT",
    "typeOfFile": "TEXT",
    "typeOfData": "ASCII",
    "sizeInBlocks": 7,
    "sizeInBytes": 13000,
}

entryF = {"status": "NEVER_USED"}

usage42 = FileSystemUsage(10, 42, 108)
usage10 = FileSystemUsage(42, 10, 108)


def test_DiskImageCliListenerQuiet_should_output_expected_messages_for_listing():
    l = DiskImageCliListenerQuiet(TypeOfDiskImageProcessing.LISTING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A.Bafter begin of file
after end of file  Post-processing message !
  x.B (deleted)after begin of file
after end of file  (unused)after begin of file
after end of fileafter end of sideSide 1
after begin of side  A.Bafter begin of file
after done
"""
        )


def test_DiskImageCliListenerQuiet_should_output_expected_messages_for_extracting():
    l = DiskImageCliListenerQuiet(TypeOfDiskImageProcessing.EXTRACTING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A.B...after begin of fileok
after end of file  Post-processing message !
  x.B (deleted)...after begin of fileignored
after end of file  (unused)...after begin of fileignored
after end of file1 file
after end of side---
Side 1
after begin of side  A.B...after begin of file
---
TOTAL
1 file
after done
"""
        )


def test_DiskImageCliListenerQuiet_should_output_expected_messages_for_updating():
    l = DiskImageCliListenerQuiet(TypeOfDiskImageProcessing.UPDATING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A.B...after begin of fileok
after end of file  Post-processing message !
  x.B (deleted)...after begin of fileignored
after end of file  (unused)...after begin of fileignored
after end of file1 file
after end of side---
Side 1
after begin of side  A.B...after begin of file
---
TOTAL
1 file
after done
"""
        )


def test_DiskImageCliListenerVerbose_should_output_expected_messages_for_listing():
    l = DiskImageCliListenerVerbose(TypeOfDiskImageProcessing.LISTING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryC)
        print("after begin of file", end="")
        l.onEndOfFile(entryC)
        print("after end of file", end="")
        l.onBeginOfFile(entryD)
        print("after begin of file", end="")
        l.onEndOfFile(entryD)
        print("after end of file", end="")
        l.onBeginOfFile(entryE)
        print("after begin of file", end="")
        l.onEndOfFile(entryE)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A       .B    BASIC   TOKEN   after begin of file    4600 Bytes      3 blocks
after end of file  Post-processing message !
  x       .B   (deleted)after begin of fileafter end of file
  C       .B    DATA    BINARY  after begin of file     130 Bytes      1 block 
after end of file  D       .B    MODULE  BINARY  after begin of file    4000 Bytes      2 blocks
after end of file  E       .TXT  TEXT    ASCII   after begin of file   13000 Bytes      7 blocks
after end of file  (unused)after begin of fileafter end of file
4 files, (42 + 10) blocks used (32.5%)
after end of side---
Side 1
after begin of side  A       .B    BASIC   TOKEN   after begin of file
after done
"""
        )


def test_DiskImageCliListenerVerbose_should_output_expected_messages_for_extracting():
    l = DiskImageCliListenerVerbose(TypeOfDiskImageProcessing.EXTRACTING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryC)
        print("after begin of file", end="")
        l.onEndOfFile(entryC)
        print("after end of file", end="")
        l.onBeginOfFile(entryD)
        print("after begin of file", end="")
        l.onEndOfFile(entryD)
        print("after end of file", end="")
        l.onBeginOfFile(entryE)
        print("after begin of file", end="")
        l.onEndOfFile(entryE)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A       .B    BASIC   TOKEN   ......after begin of file    4600 Bytes      3 blocks
after end of file  Post-processing message !
  x       .B   (deleted)        ......after begin of fileignored
after end of file  C       .B    DATA    BINARY  ......after begin of file     130 Bytes      1 block 
after end of file  D       .B    MODULE  BINARY  ......after begin of file    4000 Bytes      2 blocks
after end of file  E       .TXT  TEXT    ASCII   ......after begin of file   13000 Bytes      7 blocks
after end of file  (unused)                      ......after begin of fileignored
after end of file4 files, 13 blocks read (8.1%)
after end of side---
Side 1
after begin of side  A       .B    BASIC   TOKEN   ......after begin of file
---
TOTAL
4 files, 13 blocks read
after done
"""
        )


def test_DiskImageCliListenerVerbose_should_output_expected_messages_for_updating():
    l = DiskImageCliListenerVerbose(TypeOfDiskImageProcessing.UPDATING)
    with redirect_stdout(io.StringIO()) as out:
        l.onBeginOfSide(0)
        print("after begin of side", end="")
        l.onBeforeBeginOfFile("Pre-processing message !")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onEndOfFile(entryA)
        print("after end of file", end="")
        l.onAfterEndOfFile("Post-processing message !")
        l.onBeginOfFile(entryB)
        print("after begin of file", end="")
        l.onEndOfFile(entryB)
        print("after end of file", end="")
        l.onBeginOfFile(entryC)
        print("after begin of file", end="")
        l.onEndOfFile(entryC)
        print("after end of file", end="")
        l.onBeginOfFile(entryD)
        print("after begin of file", end="")
        l.onEndOfFile(entryD)
        print("after end of file", end="")
        l.onBeginOfFile(entryE)
        print("after begin of file", end="")
        l.onEndOfFile(entryE)
        print("after end of file", end="")
        l.onBeginOfFile(entryF)
        print("after begin of file", end="")
        l.onEndOfFile(entryF)
        print("after end of file", end="")
        l.onEndOfSide(usage42)
        print("after end of side", end="")
        l.onBeginOfSide(1)
        print("after begin of side", end="")
        l.onBeginOfFile(entryA)
        print("after begin of file", end="")
        l.onDone()
        print("after done")

        assert (
            out.getvalue()
            == """Side 0
after begin of side  Pre-processing message !
  A       .B    BASIC   TOKEN   ......after begin of file    4600 Bytes      3 blocks
after end of file  Post-processing message !
  x       .B   (deleted)        ......after begin of fileignored
after end of file  C       .B    DATA    BINARY  ......after begin of file     130 Bytes      1 block 
after end of file  D       .B    MODULE  BINARY  ......after begin of file    4000 Bytes      2 blocks
after end of file  E       .TXT  TEXT    ASCII   ......after begin of file   13000 Bytes      7 blocks
after end of file  (unused)                      ......after begin of fileignored
after end of file4 files, 13 blocks written (8.1%)
after end of side---
Side 1
after begin of side  A       .B    BASIC   TOKEN   ......after begin of file
---
TOTAL
4 files, 13 blocks written
after done
"""
        )
