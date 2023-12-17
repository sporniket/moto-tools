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
        self.blockIndex = 0

    def onBeginFileBlock(self, descriptor: LeaderDiskBlockDescriptor):
        self.blockIndex += 1
        self.currentFile = descriptor
        self.blockCount = 0
        self.fileSize = 0
        self.firstBlock = self.blockIndex

    def onDataBlock(self, block: DiskBlock):
        self.blockIndex += 1
        self.blockCount += 1
        self.fileSize += len(block.body)

    def onEndBlock(self):
        self.blockIndex += 1
        if self.verbose:
            # verbose mode
            desc = self.currentFile
            fileType = (
                "BASIC"
                if desc.fileType == 0
                else "DATA"
                if desc.fileType == 1
                else "BINARY"
            )
            fileMode = desc.fileMode
            if desc.fileType == 0:
                fileMode = "ASCII" if fileMode == 0xFFFF else "TOKEN"
            print(
                f"{desc.fileName}.{desc.fileExtension}\t{fileType}\t{fileMode}\t#{self.firstBlock}\t{self.fileSize} octets\t{self.blockCount} blocks."
            )
        elif len(self.operation) == 0:
            # non verbose list
            desc = self.currentFile
            print(f"{desc.fileName}.{desc.fileExtension}")
        self.currentFile = None

    def onError(self, message: str):
        desc = self.currentFile
        print(
            f"Error : {message}"
            if desc is None
            else f"Error on {desc.fileName}.{desc.fileExtension} : {message}"
        )


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
            metavar="<archive.fd or archive.sd>",
            type=str,
            help="the designated disk archive",
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
            help="directory where output files will be generated.",
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
        if args.create:
            disk = Disk()
            for src in sources:
                dotPos = src.rfind(".")
                fileName = os.path.basename(src.upper())
                fileExtension = ""
                fileType = 2  # binary
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
                leadBloc = LeaderDiskBlockDescriptor(
                    fileName, fileExtension, fileType, fileMode
                )
                try:
                    disk.writeBlock(leadBloc.toDiskBlock())
                    listener.onBeginFileBlock(leadBloc)
                    with open(src, "rb") as f:
                        data = f.read()
                    dataPos = 0
                    dataMax = len(data)
                    dataRemaining = dataMax
                    while dataPos < dataMax:
                        dataNextPos = (
                            dataPos + dataRemaining
                            if dataRemaining < 254
                            else dataPos + 254
                        )
                        block = DiskBlock.buildFromData(data[dataPos:dataNextPos])
                        disk.writeBlock(block)
                        listener.onDataBlock(block)
                        dataPos = dataNextPos
                        dataRemaining = dataMax - dataPos
                    disk.writeBlock(DiskBlock.buildFromData(None, TypeOfDiskBlock.EOF))
                    listener.onEndBlock()
                except OverflowError:
                    print("Too much data, abort creation.")
                    return 1
            with open(args.archive, "wb") as tar:
                tar.write(disk.rawData)

        elif args.list or args.extract:
            with open(args.archive, "rb") as tar:
                disk = Disk(tar.read())
            targetDir = os.path.dirname(args.archive)
            block = disk.nextBlock()
            while block is not None:
                if block.type == TypeOfDiskBlock.LEADER:
                    desc = LeaderDiskBlockDescriptor.buildFromDiskBlock(block.rawData)
                    listener.onBeginFileBlock(desc)
                    if args.extract:
                        fileContent = bytearray()  # initialize accumulator
                elif block.type == TypeOfDiskBlock.EOF:
                    if args.extract:
                        with open(
                            os.path.join(
                                targetDir, f"{desc.fileName}.{desc.fileExtension}"
                            ),
                            "wb",
                        ) as f:
                            f.write(fileContent)
                    listener.onEndBlock()
                else:
                    listener.onDataBlock(block)
                    if args.extract:
                        fileContent += block.body  # update accumulator
                block = disk.nextBlock()
        return 0
