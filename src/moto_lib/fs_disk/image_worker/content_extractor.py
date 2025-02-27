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


class DiskImageContentExtractor(DiskImageWorker):
    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        super().__init__(typeOfDiskImage)

    def perform(
        self,
        args,
        imageManager: SingleDiskImageManager,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
    ):
        hasTargetDirectory = args.into is not None
        if args.into is not None:
            print(f"has into : {args.into}")
            # TODO

        targetDir = args.into if hasTargetDirectory else os.path.dirname(args.archive)
        image = imageManager.image

        for i, side in enumerate(image.sides):
            listener.onBeginOfSide(i)
            sidePath = os.path.join(targetDir, f"side{i}")
            os.makedirs(sidePath)
            controller = FileSystemController(side)
            for entry in controller.listFiles():
                file = entry.toDict()
                listener.onBeginOfFile(file)
                extractedFileName = (
                    file["name"].rstrip() + "." + file["extension"].rstrip()
                )
                data = controller.readFile(entry)
                with open(os.path.join(sidePath, extractedFileName), "wb") as outf:
                    outf.write(data)
                listener.onEndOfFile(file)
            listener.onEndOfSide(controller.computeUsage())
        listener.onDone()
