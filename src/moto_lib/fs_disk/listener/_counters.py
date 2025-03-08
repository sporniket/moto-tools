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


class DiskImageCliListenerCounters:
    """Essentially keeps tracks of items to be counted."""

    def __init__(self):
        self._reset()

    def _reset(self):
        self._countSides = 0
        self._countFilesOfOneSide = 0
        self._countFilesOfAllSides = 0
        self._countBlocksOfOneSide = 0
        self._countBlocksOfAllSides = 0
        self._resetOnNextSide = False

    @property
    def countOfSides(self) -> int:
        return self._countSides

    @property
    def countOfFilesOfCurrentSide(self) -> int:
        return self._countFilesOfOneSide

    @property
    def countOfFilesOfDiskImage(self) -> int:
        return self._countFilesOfAllSides

    @property
    def countOfBlocksOfCurrentSide(self) -> int:
        return self._countBlocksOfOneSide

    @property
    def countOfBlocksOfDiskImage(self) -> int:
        return self._countBlocksOfAllSides

    def onDone(self):
        self._resetOnNextSide = True

    def onBeginOfSide(self, sidenumber: int):
        if self._resetOnNextSide:
            self._reset()
        self._countSides = self._countSides + 1
        self._countFilesOfOneSide = 0
        self._countBlocksOfOneSide = 0

    def onEndOfSide(self, usage: FileSystemUsage):
        pass

    def onBeginOfFile(
        self, data: dict[str, any]  # as provided by CatalogEntry.toDict()
    ):
        pass

    def onEndOfFile(self, data: dict[str, any]):  # as provided by CatalogEntry.toDict()
        fileIsAlive = data["status"] == CatalogEntryStatus.ALIVE.name
        if fileIsAlive:
            self._countFilesOfOneSide = self._countFilesOfOneSide + 1
            self._countFilesOfAllSides = self._countFilesOfAllSides + 1
            self._countBlocksOfOneSide = (
                self._countBlocksOfOneSide + data["sizeInBlocks"]
            )
            self._countBlocksOfAllSides = (
                self._countBlocksOfAllSides + data["sizeInBlocks"]
            )
