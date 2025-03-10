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
from ..block_descriptor import LeaderTapeBlockDescriptor


class TapeImageContentEnumerator(TapeImageWorker):
    def perform(
        self,
        args,
        imageManager: SingleTapeImageManager,
        listener: TapeImageCliListener,
    ):
        tape = imageManager.image
        block = tape.nextBlock()
        while block is not None:
            if block.type == TypeOfTapeBlock.LEADER:
                desc = LeaderTapeBlockDescriptor.buildFromTapeBlock(block.rawData)
                listener.onBeginFileBlock(desc)
            elif block.type == TypeOfTapeBlock.EOF:
                listener.onEndBlock()
            else:
                listener.onDataBlock(block)
            block = tape.nextBlock()
        return 0
