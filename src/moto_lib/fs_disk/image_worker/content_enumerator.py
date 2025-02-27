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

from .base import DiskImageWorker

from ..image import TypeOfDiskImage
from ..image_manager import SingleDiskImageManager
from ..listener import DiskImageCliListenerQuiet, DiskImageCliListenerVerbose
from ..controller import FileSystemController


class DiskImageContentEnumerator(DiskImageWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def perform(
        self,
        args,
        imageManager: SingleDiskImageManager,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
    ):
        image = imageManager.image
        for i, side in enumerate(image.sides):
            listener.onBeginOfSide(i)
            controller = FileSystemController(side)
            for entry in controller.listFiles():
                file = entry.toDict()
                listener.onBeginOfFile(file)
                listener.onEndOfFile(file)
            listener.onEndOfSide(controller.computeUsage())
        listener.onDone()
