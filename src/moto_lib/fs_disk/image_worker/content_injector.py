"""
File system on disk.
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

from .base import DiskImageWorker

from ..image import TypeOfDiskImage, DiskImage
from ..image_manager import SingleDiskImageManager
from ..listener import DiskImageCliListenerQuiet, DiskImageCliListenerVerbose
from ..catalog import TypeOfData, TypeOfDiskFile, CatalogEntryStatus
from ..controller import FileSystemController


class DiskImageContentInjector(DiskImageWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

        # setup dispatching to processor according to file extension
        self._defaultProcessors = self.processFileAsDataForBasic
        self._processors = {
            "BAS": self.processFileAsTokenizedBasic,
            "BAS,A": self.processFileAsAsciiBasic,
            "BIN": self.processFileAsBinaryModule,
            "TXT": self.processFileAsTxt,
        }

    ###########################################
    ### Interface to manage the controllers ###
    ###########################################

    def _prepareControllers(self, image: DiskImage):
        """Prepare internal state about the file system controller to use.

        Args:
            image (DiskImage): _description_
        """
        self._controllers = [FileSystemController(image.sides[i]) for i in range(4)]
        self._currentSide = 0

    @property
    def _controller(self) -> FileSystemController:
        if self._controllers is None:
            raise RuntimeError("illegal.state")
        if not self._hasController():
            raise RuntimeError("illegal.state")
        return self._controllers[self._currentSide]

    def _hasController(self) -> bool:
        if self._controllers is None:
            raise RuntimeError("illegal.state")
        if self._currentSide is None:
            raise RuntimeError("illegal.state")
        return self._currentSide < 4

    def _hasNextController(self) -> bool:
        if self._controllers is None:
            raise RuntimeError("illegal.state")
        if self._currentSide is None:
            raise RuntimeError("illegal.state")
        return (self._currentSide + 1) < 4

    def _nextController(self):
        self._currentSide = self._currentSide + 1

    ############################################
    ### Implementations of content injection ###
    ############################################

    def processFileAsTxt(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileData: bytes,
    ) -> int:
        self.writeFile(
            listener,
            fileName,
            fileExtension,
            TypeOfDiskFile.TEXT_FILE,
            TypeOfData.ASCII_DATA,
            fileData,
        )

    def processFileAsBinaryModule(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileData: bytes,
    ) -> int:
        self.writeFile(
            listener,
            fileName,
            fileExtension,
            TypeOfDiskFile.MACHINE_LANGUAGE_PROGRAM,
            TypeOfData.BINARY_DATA,
            fileData,
        )

    def processFileAsTokenizedBasic(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileData: bytes,
    ) -> int:
        self.writeFile(
            listener,
            fileName,
            fileExtension,
            TypeOfDiskFile.BASIC_PROGRAM,
            TypeOfData.BINARY_DATA,
            fileData,
        )

    def processFileAsAsciiBasic(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileData: bytes,
    ) -> int:
        self.writeFile(
            listener,
            fileName,
            "BAS",
            TypeOfDiskFile.BASIC_PROGRAM,
            TypeOfData.ASCII_DATA,
            fileData,
        )

    def processFileAsDataForBasic(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileData: bytes,
    ) -> int:
        self.writeFile(
            listener,
            fileName,
            fileExtension,
            TypeOfDiskFile.BASIC_DATA,
            TypeOfData.BINARY_DATA,
            fileData,
        )

    def writeFile(
        self,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileType: TypeOfDiskFile,
        fileMode: TypeOfData,
        fileData: bytes,
    ):
        while self._hasController():  # Still have side to try
            try:
                listener.onBeginOfFile(
                    {
                        "status": CatalogEntryStatus.ALIVE.name,
                        "name": fileName,
                        "extension": fileExtension,
                        "typeOfFile": fileType.toStringForCatalog(),
                        "typeOfData": fileMode.toStringForCatalog(fileType),
                    }
                )
                self._controller.writeFile(
                    fileData,
                    fileName,
                    fileExtension,
                    typeOfFile=fileType,
                    typeOfData=fileMode,
                )
                sizeInBytes = len(fileData)
                fullBlocks, moduloBlocks = len(fileData) // 255, len(fileData) % 255
                sizeInBlocks = fullBlocks if moduloBlocks == 0 else fullBlocks + 1
                listener.onEndOfFile(
                    {
                        "status": CatalogEntryStatus.ALIVE.name,
                        "sizeInBytes": sizeInBytes,
                        "sizeInBlocks": sizeInBlocks,
                    }
                )
                break  # done, no need to retry
            except ValueError:
                # not enough place, try next side
                listener.onAbortFile("too big")
                listener.onEndOfSide(self._controller.computeUsage())
                self._nextController()
                if not self._hasController():  # cannot try anymore
                    break
                listener.onBeginOfSide(self._currentSide)

    ###############
    ### Perform ###
    ###############

    def perform(
        self,
        args,
        imageManager: SingleDiskImageManager,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
    ):
        image = imageManager.image
        self._prepareControllers(image)

        listener.onBeginOfSide(self._currentSide)
        for src in args.sources:
            dotPos = src.rfind(".")
            fileName = os.path.basename(src.upper())

            # Either manage user decided change of side...
            if fileName == "--EOS":
                listener.onEndOfSide(self._controller.computeUsage())
                self._nextController()
                if not self._hasController():
                    break
                listener.onBeginOfSide(self._currentSide)
                continue

            # ...or process a file
            cleanSrc = src[:-2] if src[-2:].upper() == ",A" else src
            if not os.path.exists(cleanSrc):
                listener.onBeforeBeginOfFile(f"-- not found : {src}")
                continue

            if dotPos > -1:
                fileName = os.path.basename(src[0:dotPos].upper())
                fileExtension = cleanSrc[dotPos + 1 :].upper()
                fileExtensionWithOption = src[dotPos + 1 :].upper()
            else:
                fileExtension = fileExtensionWithOption = None
            if len(fileName) > 8:
                listener.onBeforeBeginOfFile(f"-- too long name : {cleanSrc}")
                continue
            if len(fileExtension) > 3:
                listener.onBeforeBeginOfFile(f"-- too long extension : {cleanSrc}")
                continue

            with open(cleanSrc, "rb") as sourceFile:
                fileData = sourceFile.read()

            # dispatch to a processor
            process = (
                self._processors[fileExtensionWithOption]
                if fileExtensionWithOption in self._processors
                else self._defaultProcessors
            )
            process(listener, fileName, fileExtension, fileData)

            if not self._hasController():  # cannot write anymore
                break

        if self._hasController():  # Successfully wrote all the files
            listener.onEndOfSide(self._controller.computeUsage())

            # goes over each remaining side in order to get expected messages
            while self._hasNextController():
                self._nextController()
                listener.onBeginOfSide(self._currentSide)
                listener.onEndOfSide(self._controller.computeUsage())

        # Finally write the image
        imageManager.save()

        listener.onDone()


class DiskImageContentInjectorWithImageInitialization(DiskImageContentInjector):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def _prepareControllers(self, image: DiskImage):
        super()._prepareControllers(image)
        for c in self._controllers:
            c.initFileSystem()
