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
            print("Creating...")
            tape = Tape()
            for src in sources:
                dotPos = src.rfind(".")
                fileType = 2  # TODO check that CSAVEM create filetype 2 / binary
                fileMode = 0
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
                    elif fileExtension == "CSV":
                        # TODO check the actual format (separator 0xD ? )
                        fileType = 1  # TODO check that file created by basic file commands have type 1 / data
                leadBloc = LeaderTapeBlockDescriptor(
                    fileName, fileExtension, fileType, fileMode
                )
                tape.writeBlock(leadBloc.toTapeBlock())
                with open(src, "rb") as f:
                    fbytes = f.read()
                tape.write(fbytes)
            with open(args.archive, "wb") as tar:
                tar.write(tape.rawData)

        elif args.list or args.extract:
            print("Listing...")
            with open(args.archive, "rb") as tar:
                tape = Tape(tar.read())
            targetDir = os.path.dirname(args.archive)
            blockCount = 0
            block = tape.nextBlock()
            fileSize = 0
            fileBlocks = 0
            while block is not None:
                blockCount += 1
                if block.type == TypeOfTapeBlock.LEADER:
                    fileSize = 0
                    fileBlocks = 0
                    desc = LeaderTapeBlockDescriptor.buildFromTapeBlock(block.rawData)
                    if args.extract:
                        fileContent = bytearray()  # initialize accumulator
                elif block.type == TypeOfTapeBlock.EOF:
                    output = (
                        f"{desc.fileName}.{desc.fileExtension}\t{desc.fileType}\t{desc.fileMode}\t{block.checksum}\t#{blockCount}\t{fileSize} octets\t{fileBlocks} blocks."
                        if args.verbose
                        else f"{desc.fileName}.{desc.fileExtension}"
                    )
                    if args.extract:
                        with open(
                            os.path.join(
                                targetDir, f"{desc.fileName}.{desc.fileExtension}"
                            ),
                            "wb",
                        ) as f:
                            f.write(fileContent)
                        if args.verbose:
                            print(output)
                    else:
                        print(output)
                else:
                    fileBlocks += 1
                    fileSize += len(block.body)
                    if args.extract:
                        fileContent += block.body  # update accumulator
                block = tape.nextBlock()

        print("Done")
