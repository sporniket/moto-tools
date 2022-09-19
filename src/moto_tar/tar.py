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


class TapeArchiveCli:
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m moto_tools_tar",
            description="Assemble, list or extract files into or from a tape archive usable with MO/TO computer emulators.",
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
            metavar="<archive.k7>",
            type=str,
            help="the designated tape archive",
        )

        parser.add_argument(
            "sources",
            metavar="<source file>",
            type=str,
            nargs="*",
            help="a list of source files",
        )

        commandGroup = parser.add_mutually_exclusive_group(required=True)
        commandGroup.add_argument(
            "-c",
            "--create",
            action="store_true",
            help=f"Assemble the designated files into the designated tape archive.",
        )
        commandGroup.add_argument(
            "-l",
            "--list",
            action="store_true",
            help=f"List all the files contained inside the designated tape archive.",
        )
        commandGroup.add_argument(
            "-x",
            "--extract",
            action="store_true",
            help=f"Extract all the files contained inside the designated tape archive.",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help=f"When present, each processed files is displayed in a tabulated format.",
        )

        parser.add_argument(
            "--into",
            help="directory where output files will be generated.",
        )
        return parser

    def __init__(self):
        pass

    def run(self) -> Optional[int]:
        args = TapeArchiveCli.createArgParser().parse_args()

        print(f"Archive : {args.archive}")

        if args.verbose:
            print("Verbose mode")

        if args.into:
            print(f"into {args.into}")

        sources = args.sources
        print(f"Given source files : {len(sources)}")
        if (len(sources) == 0) and args.create:
            print(f"Create blank tape archive...")
        else:
            for s in sources:
                print(f"Processing {s}...")

        if args.create:
            print("NOT YET IMPLEMENTED : Creating...")
        elif args.list:
            print("Listing...")
            startOfBlockSequence = bytes(
                [
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x01,
                    0x3C,
                    0x5A,
                ]
            )
            with open(args.archive, "rb") as tar:
                tarContent = tar.read()
                startFrom = 0
                blockCount = 0
                while startFrom < len(tarContent):
                    next = tarContent.find(startOfBlockSequence, startFrom)
                    if next == -1:
                        startFrom = len(tarContent)
                    else:
                        startFrom = next + len(startOfBlockSequence)
                        if (
                            tarContent[startFrom] == 0
                            and tarContent[startFrom + 1] == 16
                        ):
                            fileName = tarContent[
                                startFrom + 2 : startFrom + 10
                            ].decode("utf-8")
                            fileExtension = tarContent[
                                startFrom + 10 : startFrom + 13
                            ].decode("utf-8")
                            fileType = tarContent[startFrom + 13]
                            fileMode = (
                                tarContent[startFrom + 14] * 256
                                + tarContent[startFrom + 15]
                            )
                            checksum = tarContent[startFrom + 16]
                            print(
                                f"{fileName}.{fileExtension} Type {fileType} Mode {fileMode} Checksum {checksum} at block #{blockCount}"
                            )
                        blockCount = blockCount + 1

        elif args.extract:
            print("NOT YET IMPLEMENTED : Extracting...")

        print("Done")
