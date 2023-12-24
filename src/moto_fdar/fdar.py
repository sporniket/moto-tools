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

from moto_lib import *


class DiskArchiveCliListener:
    def __init__(self, operation: str, verbose: bool = False):
        """Initialize the listener.

        Args:
            operation (str): "Adding", "Extracting" or ""
            verbose (bool, optional): Enable verbose mode or not. Defaults to disabled.
        """
        self.operation = operation
        self.verbose = verbose


class DiskArchiveCli:
    @staticmethod
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m moto_fdar",
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
            metavar="<archive.fd>",
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

        parser.add_argument(
            "--reference",
            metavar="<ref_archive.fd>",
            help="The archive will created starting from a duplicate of the reference archive ; source files will be added to that duplicate.",
        )
        return parser

    def __init__(self):
        pass

    def run(self) -> int:
        args = DiskArchiveCli.createArgParser().parse_args()
        sources = args.sources
        listener = DiskArchiveCliListener(
            "adding" if args.create else "extracting" if args.extract else "",
            args.verbose,
        )
        ### assess type of archive
        archive = args.archive
        dotPos = archive.rfind(".")
        if dotPos < 0:
            raise ValueError(
                f"'{archive}' MUST have an extension, either '.fd' or '.sd'."
            )
        archiveExtension = archive[dotPos + 1 :].lower()
        typeOfArchive = None
        if archiveExtension == "sd":
            typeOfArchive = TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE
        elif archiveExtension == "fd":
            typeOfArchive = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE
        else:
            raise ValueError(
                f"'{archive}' MUST have an extension, either '.fd' or '.sd'."
            )

        ### process target folder
        hasTargetDirectory = False
        if len(args.into) > 0:
            print(f"has into : {args.into}")
            # TODO

        if args.create:
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
            with open(args.archive, "wb") as fdar:
                fdar.write(disk.rawData)

        elif args.extract:
            with open(args.archive, "rb") as fdar:
                # TODO
                raise RuntimeError("NOT IMPLEMENTED")
            targetDir = (
                args.into if hasTargetDirectory else os.path.dirname(args.archive)
            )
        
        elif args.list:
            with open(args.archive, "rb") as fdar:
                # TODO
                raise RuntimeError("NOT IMPLEMENTED")
                # **event** : size of archive, type (emulator/sddrive), number of sides

                # steps
                # * for each disk side (a.k.a. 'unit')
                #   * **event** : begin side 's' ('unit #s')
                #   * seek to catalog (track 20, from sector 3 to 16)
                #   * for each entry from the catalog (up to 8 entries per sector --> up to 112 entries for a side)
                #     * IF entry is valid (not deleted, not empty,...)
                #       * **event** : catalog entry
                #   * **event** : done catalogue
                #   * **event** : done side
                # * **event** done archive
        return 0
