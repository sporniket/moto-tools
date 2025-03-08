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

from .block import TapeBlock
from .block_descriptor import LeaderTapeBlockDescriptor


class TapeArchiveCliListener(ABC):
    def __init__(self, operation: str):
        """Initialize the listener.

        Args:
            operation (str): "Adding", "Extracting" or ""
            verbose (bool, optional): Enable verbose mode or not. Defaults to disabled.
        """
        self.operation = operation
        self.blockIndex = 0

    def onBeginFileBlock(self, descriptor: LeaderTapeBlockDescriptor):
        self.blockIndex += 1
        self.currentFile = descriptor
        self.blockCount = 0
        self.fileSize = 0
        self.firstBlock = self.blockIndex

    def onDataBlock(self, block: TapeBlock):
        self.blockIndex += 1
        self.blockCount += 1
        self.fileSize += len(block.body)

    @abstractmethod
    def printOnEndBlock(self):
        pass

    def onEndBlock(self):
        self.blockIndex += 1
        self.printOnEndBlock()
        self.currentFile = None

    def onError(self, message: str):
        desc = self.currentFile
        print(
            f"Error : {message}"
            if desc is None
            else f"Error on {desc.fileName}.{desc.fileExtension} : {message}"
        )


class TapeArchiveCliListenerVerbose(TapeArchiveCliListener):
    def printOnEndBlock(self):
        desc = self.currentFile
        fileType = (
            "BASIC"
            if desc.fileType == 0
            else "DATA" if desc.fileType == 1 else "BINARY"
        )
        fileMode = desc.fileMode
        if desc.fileType == 0:
            fileMode = "ASCII" if fileMode == 0xFFFF else "TOKEN"
        print(
            f"{desc.fileName}.{desc.fileExtension}\t{fileType}\t{fileMode}\t#{self.firstBlock}\t{self.fileSize} octets\t{self.blockCount} blocks."
        )


class TapeArchiveCliListenerQuiet(TapeArchiveCliListener):
    def printOnEndBlock(self):
        desc = self.currentFile
        print(f"{desc.fileName}.{desc.fileExtension}")
