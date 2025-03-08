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

from abc import ABC, abstractmethod

from moto_lib.fs_disk.controller import FileSystemUsage
from moto_lib.fs_disk.catalog import CatalogEntryStatus

from .consts import TypeOfDiskImageProcessing
from ._counters import DiskImageCliListenerCounters


class DiskImageCliListener(ABC):
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

    ###############
    ### on done ###
    ###############

    @abstractmethod
    def printOnDone(self):
        pass

    def onDone(self):
        self._counter.onDone()
        self._printReturnLineIfNeeded()
        self.printOnDone()

    ########################
    ### on begin of side ###
    ########################

    @abstractmethod
    def printOnBeginOfSide(self, sidenumber: int):
        pass

    def onBeginOfSide(self, sidenumber: int):
        self._counter.onBeginOfSide(sidenumber)
        self._printReturnLineIfNeeded()
        self.printOnBeginOfSide(sidenumber)

    ######################
    ### on end of side ###
    ######################

    @abstractmethod
    def printOnEndOfSide(self, usage: FileSystemUsage):
        pass

    def onEndOfSide(self, usage: FileSystemUsage):
        self._counter.onEndOfSide(usage)
        self._printReturnLineIfNeeded()
        self.printOnEndOfSide(usage)

    ########################
    ### on begin of file ###
    ########################

    @abstractmethod
    def printOnBeginOfFile(
        self, data: dict[str, any]  # as provided by CatalogEntry.toDict()
    ):
        pass

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
        self.printOnBeginOfFile(data)

    ######################
    ### on end of file ###
    ######################
    @abstractmethod
    def printOnEndOfFile(self, data: dict[str, any]):
        pass

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
        self.printOnEndOfFile(data)

    #################
    ### messagers ###
    #################

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
