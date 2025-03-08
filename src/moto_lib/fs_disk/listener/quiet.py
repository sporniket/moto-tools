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

from abc import ABC
from enum import Enum

from moto_lib.fs_disk.controller import FileSystemUsage
from moto_lib.fs_disk.catalog import CatalogEntryStatus

from .consts import FINAL_NONE, FINAL_S, TypeOfDiskImageProcessing
from .listener import DiskImageCliListener


class DiskImageCliListenerQuiet(DiskImageCliListener):

    def printOnDone(self):
        if (
            self._processing != TypeOfDiskImageProcessing.LISTING
            and self._counter.countOfSides > 0
        ):
            print("---")
            print("TOTAL")
            print(
                f"{self._counter.countOfFilesOfDiskImage} file{(FINAL_S if self._counter.countOfFilesOfDiskImage != 1 else FINAL_NONE)}"
            )

    def printOnBeginOfSide(self, sidenumber: int):
        if (
            self._processing != TypeOfDiskImageProcessing.LISTING
            and self._counter.countOfSides > 1
        ):
            print("---")
        print(f"Side {sidenumber}")

    def printOnEndOfSide(self, usage: FileSystemUsage):
        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print(
                f"{self._counter.countOfFilesOfCurrentSide} file{FINAL_S if self._counter.countOfFilesOfCurrentSide != 1 else FINAL_NONE}"
            )

    def printOnBeginOfFile(
        self, data: dict[str, any]  # as provided by CatalogEntry.toDict()
    ):
        """Process 'begin of file' events.

        The event MUST contains following properties :
        * `status` : CatalogEntryStatus.name of the file
        * `name` : the file name (8 chars at most)
        * `extension` : the file extension (3 chars at most)
        * `typeOfFile` : TypeOfFile.toStringForCatalog()
        * `typeOfData` : TypeOfData.toStringForCatalog()

        Args:
            data (dict[str, any]): The event description
        """
        if data["status"] == CatalogEntryStatus.NEVER_USED.name:
            print(f"  (unused)", end="")
        else:
            name, extension = data["name"], data["extension"]
            print(f"  {name.rstrip()}.{extension.rstrip()}", end="")
            if data["status"] == CatalogEntryStatus.DELETED.name:
                print(" (deleted)", end="")
        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print("...", end="")

        self._needReturnLine = True

    def printOnEndOfFile(
        self, data: dict[str, any]
    ):  # as provided by CatalogEntry.toDict()
        """Process 'end of file' events.

        The event MUST contains following properties :
        * `status` : CatalogEntryStatus.name of the file
        * `sizeInBytes` : size in bytes
        * `sizeInBlocks` : size in blocks

        Args:
            data (dict[str, any]): The event description
        """
        fileIsAlive = data["status"] == CatalogEntryStatus.ALIVE.name

        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print("ok" if fileIsAlive else "ignored")
            self._needReturnLine = False
        else:
            self._printReturnLineIfNeeded()
