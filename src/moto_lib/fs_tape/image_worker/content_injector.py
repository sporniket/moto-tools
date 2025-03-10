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

from .base import TapeImageWorker

from ..image_manager import SingleTapeImageManager
from ..listeners import TapeImageCliListener
from ..consts import TypeOfTapeBlock
from ..block import TapeBlock
from ..block_descriptor import LeaderTapeBlockDescriptor


class TapeImageContentInjector(TapeImageWorker):
    def perform(
        self,
        args,
        imageManager: SingleTapeImageManager,
        listener: TapeImageCliListener,
    ):
        tape = imageManager.image
        for src in args.sources:
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
                elif fileExtension == "CSV":
                    # TODO check the actual format (separator 0xD ? )
                    fileType = 1  # TODO check that file created by basic file commands have type 1 / data
            leadBloc = LeaderTapeBlockDescriptor(
                fileName, fileExtension, fileType, fileMode
            )
            try:
                tape.writeBlock(leadBloc.toTapeBlock())
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
                    block = TapeBlock.buildFromData(data[dataPos:dataNextPos])
                    tape.writeBlock(block)
                    listener.onDataBlock(block)
                    dataPos = dataNextPos
                    dataRemaining = dataMax - dataPos
                tape.writeBlock(TapeBlock.buildFromData(None, TypeOfTapeBlock.EOF))
                listener.onEndBlock()
            except OverflowError:
                print("Too much data, abort creation.")
                return 1
        imageManager.save()
        return 0
