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
            action="store_true",
            help=f"Assemble the designated files into the designated disk archive.",
        )
        commandGroup.add_argument(
            "-t",
            "--list",
            action="store_true",
            help=f"List all the files contained inside the designated disk archive.",
        )
        commandGroup.add_argument(
            "-x",
            "--extract",
            action="store_true",
            help=f"Extract all the files contained inside the designated disk archive.",
        )
        commandGroup.add_argument(
            "-r",
            "--append",
            action="store_true",
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
        pass

    def run(self) -> int:
        args = DiskArchiveCli.createArgParser().parse_args()
        sources = args.sources
        typeOfProcessing = (
            TypeOfProcessing.LISTING
            if args.list
            else (
                TypeOfProcessing.EXTRACTING
                if args.extract
                else TypeOfProcessing.UPDATING
            )
        )
        listener = (
            DiskImageCliListenerVerbose(typeOfProcessing)
            if args.verbose
            else DiskImageCliListenerQuiet(typeOfProcessing)
        )

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
        hasTargetDirectory = False
        if args.into is not None:
            print(f"has into : {args.into}")
            # TODO

        if args.create:
            raise RuntimeError("not.implemented.yet")
            # TODO prepare working file -- optionnally using a reference archive file
            for src in sources:
                dotPos = src.rfind(".")
                fileName = os.path.basename(src.upper())
                fileExtension = ""
                fileType = TypeOfDiskFile.BASIC_DATA
                if dotPos > -1:
                    fileName = os.path.basename(src[0:dotPos].upper())
                    if len(fileName) > 8:
                        fileName = fileName[0:8]
                    fileExtension = src[dotPos + 1 :].upper()
                    if fileExtension == "BAS,A":
                        fileExtension = "BAS"
                        fileType = 0  # basic
                        fileMode = 0xFFFF  # -1, ascii listing
                        src = src[:-2]
                    elif fileExtension == "BAS":
                        fileType = 0  # basic
                    elif fileType == "LST":
                        # TODO converts on the fly into ASCII BAS ?
                        pass
                    # TODO other things ?
                try:
                    # TODO write file into blocs
                    # TODO commit file into FAT and CATALOG
                    raise OverflowError("WRITE NOT IMPLEMENTED")
                except OverflowError:
                    print("Too much data, abort creation.")
                    return 1
            with open(args.archive, "wb") as sdar:
                sdar.write(disk.rawData)

        elif args.extract:
            raise RuntimeError("not.implemented.yet")
            with open(args.archive, "rb") as sdar:
                # TODO
                pass
            targetDir = (
                args.into if hasTargetDirectory else os.path.dirname(args.archive)
            )

        elif args.list:
            with open(args.archive, "rb") as sdar:
                # TODO
                disk = DiskImage(
                    sdar.read(), typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
                )
                # **event** : size of archive, type (emulator/sddrive), number of sides

                # steps
                # * for each disk side (a.k.a. 'unit')
                for i, side in enumerate(disk.sides):
                    listener.onBeginOfSide(i)
                    controller = FileSystemController(side)
                    for entry in controller.listFiles():
                        file = entry.toDict()
                        listener.onBeginOfFile(file)
                        listener.onEndOfFile(file)
                    listener.onEndOfSide(controller.computeUsage())
                listener.onDone()
        return 0
