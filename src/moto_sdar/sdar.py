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

from abc import ABC, abstractmethod
from argparse import ArgumentParser, RawDescriptionHelpFormatter, FileType

from typing import List, Union, Optional
from enum import Enum

from moto_lib.fs_disk.controller import FileSystemController
from moto_lib.fs_disk.image import DiskImage, DiskSide, TypeOfDiskImage
from moto_lib.fs_disk.image_manager import (
    SingleDiskImageManager,
    DiskImageFromDiskManager,
)
from moto_lib.fs_disk.image_worker import (
    DiskImageContentEnumerator,
    DiskImageContentExtractor,
    DiskImageContentInjector,
    DiskImageContentInjectorWithImageInitialization,
)
from moto_lib.fs_disk.catalog import TypeOfDiskFile, TypeOfData, CatalogEntryStatus
from moto_lib.fs_disk.listener import (
    DiskImageCliListenerQuiet,
    DiskImageCliListenerVerbose,
    TypeOfDiskImageProcessing,
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
            "--add",
            dest="action",
            action="store_const",
            const="add",
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
        self._typeOfArchive = typeOfArchive = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        self._archiveExtension = "sd"
        self._imageManagers = {
            "add": DiskImageFromDiskManager,
            "create": SingleDiskImageManager,
            "extract": DiskImageFromDiskManager,
            "list": DiskImageFromDiskManager,
        }
        self._workers = {
            "add": DiskImageContentInjector(typeOfArchive),
            "create": DiskImageContentInjectorWithImageInitialization(typeOfArchive),
            "extract": DiskImageContentExtractor(typeOfArchive),
            "list": DiskImageContentEnumerator(typeOfArchive),
        }
        self._typesOfProcessing = {
            "add": TypeOfDiskImageProcessing.UPDATING,
            "create": TypeOfDiskImageProcessing.UPDATING,
            "extract": TypeOfDiskImageProcessing.EXTRACTING,
            "list": TypeOfDiskImageProcessing.LISTING,
        }

    def createListener(
        self, args
    ) -> DiskImageCliListenerVerbose or DiskImageCliListenerQuiet:
        if args.action not in self._typesOfProcessing:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")
        typeOfProcessing = self._typesOfProcessing[args.action]

        return (
            DiskImageCliListenerVerbose(typeOfProcessing)
            if args.verbose
            else DiskImageCliListenerQuiet(typeOfProcessing)
        )

    def createImageManager(self, args) -> SingleDiskImageManager:
        if args.action not in self._imageManagers:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")
        return self._imageManagers[args.action](self._typeOfArchive, args.archive)

    def run(self) -> int:
        args = DiskArchiveCli.createArgParser().parse_args()

        listener = self.createListener(args)

        ### assess type of archive
        archive = args.archive
        dotPos = archive.rfind(".")
        if dotPos < 0:
            raise ValueError(f"error.file.name.must.have.extension:{archive}")
        archiveExtension = archive[dotPos + 1 :].lower()
        if archiveExtension != self._archiveExtension:
            raise ValueError(f"error.file.name.extension.should.be.sd:{archive}")

        imageManager = self.createImageManager(args)

        ### process target folder
        if args.action not in self._workers:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")

        self._workers[args.action].perform(args, imageManager, listener)
        return 0
