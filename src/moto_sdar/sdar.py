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
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, FileType

from typing import List, Union, Optional
from enum import Enum

from moto_lib.fs_disk.controller import FileSystemController
from moto_lib.fs_disk.image import DiskImage, DiskSide, TypeOfDiskImage
from moto_lib.fs_disk.catalog import TypeOfDiskFile, TypeOfData, CatalogEntryStatus
from moto_lib.listener.dar_listener import (
    DiskImageCliListenerQuiet,
    DiskImageCliListenerVerbose,
    TypeOfProcessing,
)


class DiskArchiveCli:
    @staticmethod
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m moto_sdar",
            description="Assemble, list or extract files into or from a disk archive usable with MO/TO computer emulators.",
            epilog="""---
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
""",
            formatter_class=RawDescriptionHelpFormatter,
            allow_abbrev=False,
        )

        # Add the arguments
        parser.add_argument(
            "archive",
            metavar="<archive.sd>",
            type=str,
            help="the designated disk archive",
        )

        parser.add_argument(
            "sources",
            metavar="<source files...>",
            type=str,
            nargs="*",
            help="a list of source files",
        )

        commandGroup = parser.add_mutually_exclusive_group(required=True)
        commandGroup.add_argument(
            "-c",
            "--create",
            dest="action",
            action="store_const",
            const="create",
            help=f"Assemble the designated files into the designated disk archive.",
        )
        commandGroup.add_argument(
            "-t",
            "--list",
            dest="action",
            action="store_const",
            const="list",
            help=f"List all the files contained inside the designated disk archive.",
        )
        commandGroup.add_argument(
            "-x",
            "--extract",
            dest="action",
            action="store_const",
            const="extract",
            help=f"Extract all the files contained inside the designated disk archive.",
        )
        commandGroup.add_argument(
            "-r",
            "--append",
            dest="action",
            action="store_const",
            const="append",
            help=f"Add the designated files into the already existing designated disk archive.",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help=f"When present, each processed files is displayed in a tabulated format.",
        )

        parser.add_argument(
            "--into",
            metavar="<directory>",
            help="Directory where output files will be generated.",
        )

        return parser

    def __init__(self):
        typeOfArchive = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        self._workers = {
            "create": DiskArchiveCreator(typeOfArchive),
            "extract": DiskArchiveExtractor(typeOfArchive),
            "list": DiskArchiveListor(typeOfArchive),
        }
        self._typesOfProcessing = {
            "create": TypeOfProcessing.UPDATING,
            "extract": TypeOfProcessing.EXTRACTING,
            "list": TypeOfProcessing.LISTING,
        }

    def createListener(self, args):
        if args.action not in self._typesOfProcessing:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")
        typeOfProcessing = self._typesOfProcessing[args.action]

        return (
            DiskImageCliListenerVerbose(typeOfProcessing)
            if args.verbose
            else DiskImageCliListenerQuiet(typeOfProcessing)
        )

    def run(self) -> int:
        args = DiskArchiveCli.createArgParser().parse_args()

        listener = self.createListener(args)

        ### assess type of archive
        archive = args.archive
        dotPos = archive.rfind(".")
        if dotPos < 0:
            raise ValueError(f"error.file.name.must.have.extension:{archive}")
        archiveExtension = archive[dotPos + 1 :].lower()
        typeOfArchive = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        if archiveExtension != "sd":
            raise ValueError(f"error.file.name.extension.should.be.sd:{archive}")

        ### process target folder
        if args.action not in self._workers:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")

        self._workers[args.action].perform(args, listener)
        return 0


class DiskArchiveWorker:
    """Base class to an implementation working on a disk archive."""

    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        if typeOfDiskImage is None:
            raise ValueError("error.undefined.type.of.disk.image")
        self._typeOfDiskImage = typeOfDiskImage

    def perform(
        self, args, listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose
    ):
        pass


class DiskArchiveListor(DiskArchiveWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def perform(
        self, args, listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose
    ):
        with open(args.archive, "rb") as sdar:
            disk = DiskImage(
                sdar.read(), typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
            )

            for i, side in enumerate(disk.sides):
                listener.onBeginOfSide(i)
                controller = FileSystemController(side)
                for entry in controller.listFiles():
                    file = entry.toDict()
                    listener.onBeginOfFile(file)
                    listener.onEndOfFile(file)
                listener.onEndOfSide(controller.computeUsage())
            listener.onDone()


class DiskArchiveExtractor(DiskArchiveWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def perform(
        self, args, listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose
    ):
        hasTargetDirectory = args.into is not None
        if args.into is not None:
            print(f"has into : {args.into}")
            # TODO

        targetDir = args.into if hasTargetDirectory else os.path.dirname(args.archive)
        with open(args.archive, "rb") as sdar:
            disk = DiskImage(
                sdar.read(), typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
            )

            for i, side in enumerate(disk.sides):
                listener.onBeginOfSide(i)
                sidePath = os.path.join(targetDir, f"side{i}")
                os.makedirs(sidePath)
                controller = FileSystemController(side)
                for entry in controller.listFiles():
                    file = entry.toDict()
                    listener.onBeginOfFile(file)
                    extractedFileName = (
                        file["name"].rstrip() + "." + file["extension"].rstrip()
                    )
                    data = controller.readFile(entry)
                    with open(os.path.join(sidePath, extractedFileName), "wb") as outf:
                        outf.write(data)
                    listener.onEndOfFile(file)
                listener.onEndOfSide(controller.computeUsage())
            listener.onDone()


class DiskArchiveCreator(DiskArchiveWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def perform(
        self, args, listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose
    ):
        image = DiskImage(bytes(), typeOfDiskImage=self._typeOfDiskImage)
        controllers = [FileSystemController(image.sides[i]) for i in range(4)]
        for c in controllers:
            c.initFileSystem()

        currentSide = 0
        listener.onBeginOfSide(currentSide)
        sources = args.sources
        for src in sources:
            dotPos = src.rfind(".")
            fileName = os.path.basename(src.upper())
            fileExtension = ""
            # by default a file is binary data
            fileType = TypeOfDiskFile.BASIC_DATA
            fileMode = TypeOfData.BINARY_DATA
            if dotPos > -1:
                fileName = os.path.basename(src[0:dotPos].upper())
                if fileName == "--EOS":
                    currentSide = currentSide + 1
                    continue
                if len(fileName) > 8:
                    fileName = fileName[0:8]
                fileExtension = src[dotPos + 1 :].upper()
                # TODO implement a filter chain, that MAY alter the content/name of the target filename (lst)
                if fileExtension == "BAS,A":
                    fileType = TypeOfDiskFile.BASIC_PROGRAM
                    fileMode = TypeOfData.ASCII_DATA
                    fileExtension = "BAS"
                    src = src[:-2]
                elif fileExtension == "BAS":
                    fileType = TypeOfDiskFile.BASIC_PROGRAM
                    fileMode = TypeOfData.ASCII_DATA
                elif fileExtension == "LST":
                    fileType = TypeOfDiskFile.BASIC_PROGRAM
                    fileMode = TypeOfData.ASCII_DATA
                    # TODO converts on the fly into ASCII BAS
                elif fileExtension == "TXT":
                    fileType = TypeOfDiskFile.TEXT_FILE
                    fileMode = TypeOfData.ASCII_DATA
                elif fileExtension == "BIN":
                    fileType = TypeOfDiskFile.MACHINE_LANGUAGE_PROGRAM
                # TODO other things ?
            # notify event
            with open(src, "rb") as sourceFile:
                fileData = sourceFile.read()
            currentSide = self.writeFile(
                currentSide,
                listener,
                fileName,
                fileExtension,
                fileType,
                fileMode,
                controllers,
                fileData,
            )
            if currentSide >= 4:  # cannot write anymore
                break
        if currentSide < 4:  # Successfully wrote all the files
            listener.onEndOfSide(controllers[currentSide].computeUsage())
            currentSide = currentSide + 1
            while currentSide < 4:  # skip all remaining sides
                listener.onBeginOfSide(currentSide)
                listener.onEndOfSide(controllers[currentSide].computeUsage())
                currentSide = currentSide + 1

        with open(args.archive, "wb") as sdar:
            for s in image.sides:
                for t in s.tracks:
                    for sector in t.sectors:
                        sdar.write(sector.dataOfSector)

        listener.onDone()

    def writeFile(
        self,
        currentSide: int,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
        fileName: str,
        fileExtension: str,
        fileType: TypeOfDiskFile,
        fileMode: TypeOfData,
        controllers,
        fileData: bytes,
    ) -> int:
        while currentSide < 4:  # Still have side to try
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
                controllers[currentSide].writeFile(
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
                listener.onEndOfSide(controllers[currentSide].computeUsage())
                currentSide = currentSide + 1
                if currentSide >= 4:  # cannot try anymore
                    break
                listener.onBeginOfSide(currentSide)
        return currentSide
