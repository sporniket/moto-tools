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

from enum import Enum

from ..fs_disk.controller import FileSystemUsage
from ..fs_disk.catalog import CatalogEntryStatus


# Python < 3.12 forbids f-strings like `f"{"what" if condition else "ever"}"`
FINAL_S = "s"
FINAL_SPACE = " "
FINAL_NONE = ""
PADDING_8 = "        "
PADDING_22 = "                      "
VERB_READ = "read"
VERB_WRITTEN = "written"


class TypeOfDiskImageProcessing(Enum):
    LISTING = 0
    EXTRACTING = 1  # for extracting files from an image
    UPDATING = 2  # for putting files into an image


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


class DiskImageCliListenerQuiet:
    def __init__(
        self,
        typeOfProcessing: TypeOfDiskImageProcessing = TypeOfDiskImageProcessing.LISTING,
    ):
        self._processing = typeOfProcessing
        self._needReturnLine = False
        self._counter = DiskImageCliListenerCounters()

    def _printReturnLineIfNeeded(self):
        if self._needReturnLine:
            print()
            self._needReturnLine = False

    def onDone(self):
        self._counter.onDone()

        self._printReturnLineIfNeeded()
        if (
            self._processing != TypeOfDiskImageProcessing.LISTING
            and self._counter.countOfSides > 0
        ):
            print("---")
            print("TOTAL")
            print(
                f"{self._counter.countOfFilesOfDiskImage} file{(FINAL_S if self._counter.countOfFilesOfDiskImage != 1 else FINAL_NONE)}"
            )

    def onBeginOfSide(self, sidenumber: int):
        self._counter.onBeginOfSide(sidenumber)

        self._printReturnLineIfNeeded()
        if (
            self._processing != TypeOfDiskImageProcessing.LISTING
            and self._counter.countOfSides > 1
        ):
            print("---")
        print(f"Side {sidenumber}")

    def onEndOfSide(self, usage: FileSystemUsage):
        self._counter.onEndOfSide(usage)

        self._printReturnLineIfNeeded()
        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print(
                f"{self._counter.countOfFilesOfCurrentSide} file{FINAL_S if self._counter.countOfFilesOfCurrentSide != 1 else FINAL_NONE}"
            )

    def onBeginOfFile(
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
        self._counter.onBeginOfFile(data)

        self._printReturnLineIfNeeded()
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

    def onEndOfFile(self, data: dict[str, any]):  # as provided by CatalogEntry.toDict()
        """Process 'end of file' events.

        The event MUST contains following properties :
        * `status` : CatalogEntryStatus.name of the file
        * `sizeInBytes` : size in bytes
        * `sizeInBlocks` : size in blocks

        Args:
            data (dict[str, any]): The event description
        """
        self._counter.onEndOfFile(data)

        fileIsAlive = data["status"] == CatalogEntryStatus.ALIVE.name

        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print("ok" if fileIsAlive else "ignored")
            self._needReturnLine = False
        else:
            self._printReturnLineIfNeeded()

    def onBeforeBeginOfFile(self, fullyDefinedMessage: str):
        """Notify of a pre-processing happening before starting to work on a file"""
        print(f"  {fullyDefinedMessage}")
        self._needReturnLine = False

    def onAfterEndOfFile(self, fullyDefinedMessage: str):
        """Notify of a post-processing happening after having finished to work on a file"""
        print(f"  {fullyDefinedMessage}")
        self._needReturnLine = False

    def onAbortFile(self, fullyDefinedMessage: str):
        """A file has been started, but the process is interrupted for the given reason"""
        print(fullyDefinedMessage)
        self._needReturnLine = False


class DiskImageCliListenerVerbose:
    def __init__(
        self,
        typeOfProcessing: TypeOfDiskImageProcessing = TypeOfDiskImageProcessing.LISTING,
    ):
        self._processing = typeOfProcessing
        self._needReturnLine = False
        self._counter = DiskImageCliListenerCounters()

    def _printReturnLineIfNeeded(self):
        if self._needReturnLine:
            print()
            self._needReturnLine = False

    def onDone(self):
        self._counter.onDone()

        self._printReturnLineIfNeeded()
        if (
            self._processing != TypeOfDiskImageProcessing.LISTING
            and self._counter.countOfSides > 0
        ):
            print("---")
            print("TOTAL")
            print(
                f"{self._counter.countOfFilesOfDiskImage} file{FINAL_S if self._counter.countOfFilesOfDiskImage != 1 else FINAL_NONE}, {self._counter.countOfBlocksOfDiskImage} block{FINAL_S if self._counter.countOfBlocksOfDiskImage != 1 else FINAL_NONE} {VERB_READ if self._processing == TypeOfDiskImageProcessing.EXTRACTING else VERB_WRITTEN}"
            )

    def onBeginOfSide(self, sidenumber: int):
        self._counter.onBeginOfSide(sidenumber)

        self._printReturnLineIfNeeded()
        if self._counter.countOfSides > 1:
            print("---")
        print(f"Side {sidenumber}")

    def onEndOfSide(self, usage: FileSystemUsage):
        self._counter.onEndOfSide(usage)

        self._printReturnLineIfNeeded()
        print(
            (
                "empty"
                if self._counter.countOfFilesOfCurrentSide == 0
                else f"{self._counter.countOfFilesOfCurrentSide} file{FINAL_S if self._counter.countOfFilesOfCurrentSide != 1 else FINAL_NONE}"
            ),
            end="",
        )
        totalUse = usage.reserved + usage.used
        totalBlock = totalUse + usage.free
        if self._processing == TypeOfDiskImageProcessing.LISTING:
            print(
                f", ({usage.reserved} + {usage.used}) block{FINAL_S if (totalBlock) != 1 else FINAL_NONE} used ({(totalUse/totalBlock):.1%})"
            )
        elif self._processing == TypeOfDiskImageProcessing.EXTRACTING:
            print(
                f", {self._counter.countOfBlocksOfCurrentSide} block{FINAL_S if (self._counter.countOfBlocksOfCurrentSide) != 1 else FINAL_NONE} read ({(self._counter.countOfBlocksOfCurrentSide/totalBlock):.1%})"
            )
        elif self._processing == TypeOfDiskImageProcessing.UPDATING:
            print(
                f", {self._counter.countOfBlocksOfCurrentSide} block{FINAL_S if (self._counter.countOfBlocksOfCurrentSide) != 1 else FINAL_NONE} written ({(self._counter.countOfBlocksOfCurrentSide/totalBlock):.1%})"
            )
        else:
            print()

    def onBeginOfFile(
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
        self._counter.onBeginOfFile(data)
        isListing = self._processing == TypeOfDiskImageProcessing.LISTING

        self._printReturnLineIfNeeded()
        if data["status"] == CatalogEntryStatus.NEVER_USED.name:
            print(f"  (unused){FINAL_NONE if isListing else PADDING_22}", end="")
        else:
            name, extension = data["name"], data["extension"]
            print(f"  {name}.{extension}", end="")
            if data["status"] == CatalogEntryStatus.DELETED.name:
                print(f" (deleted){FINAL_NONE if isListing else PADDING_8}", end="")
            else:
                typeOfFile, typeOfData = data["typeOfFile"], data["typeOfData"]
                print(f"  {typeOfFile:8}{typeOfData:8}", end="")
        if self._processing != TypeOfDiskImageProcessing.LISTING:
            print("......", end="")

        self._needReturnLine = True

    def onEndOfFile(self, data: dict[str, any]):  # as provided by CatalogEntry.toDict()
        """Process 'end of file' events.

        The event MUST contains following properties :
        * `status` : CatalogEntryStatus.name of the file
        * `sizeInBytes` : size in bytes
        * `sizeInBlocks` : size in blocks

        Args:
            data (dict[str, any]): The event description
        """
        self._counter.onEndOfFile(data)

        fileIsAlive = data["status"] == CatalogEntryStatus.ALIVE.name

        if fileIsAlive:
            sizeInBytes, sizeInBlocks = data["sizeInBytes"], data["sizeInBlocks"]
            print(
                f"  {sizeInBytes:6d} Byte{FINAL_S if sizeInBytes != 1 else FINAL_SPACE}    {sizeInBlocks:3d} block{FINAL_S if sizeInBlocks != 1 else FINAL_SPACE}"
            )
            self._needReturnLine = False
        else:
            if self._processing != TypeOfDiskImageProcessing.LISTING:
                print("ignored")
                self._needReturnLine = False

    def onBeforeBeginOfFile(self, fullyDefinedMessage: str):
        """Notify of a pre-processing happening before starting to work on a file"""
        print(f"  {fullyDefinedMessage}")

    def onAfterEndOfFile(self, fullyDefinedMessage: str):
        """Notify of a post-processing happening after having finished to work on a file"""
        print(f"  {fullyDefinedMessage}")

    def onAbortFile(self, fullyDefinedMessage: str):
        """A file has been started, but the process is interrupted for the given reason"""
        print(fullyDefinedMessage)
        self._needReturnLine = False
