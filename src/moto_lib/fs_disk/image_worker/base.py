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

from ..image import TypeOfDiskImage
from ..image_manager import SingleDiskImageManager
from ..listener import DiskImageCliListenerQuiet, DiskImageCliListenerVerbose


class DiskImageWorker:
    """Base class to an implementation working on a disk image."""

    def __init__(self, typeOfDiskImage: TypeOfDiskImage):
        if typeOfDiskImage is None:
            raise ValueError("error.undefined.type.of.disk.image")
        self._typeOfDiskImage = typeOfDiskImage

    def perform(
        self,
        args,
        imageManager: SingleDiskImageManager,
        listener: DiskImageCliListenerQuiet or DiskImageCliListenerVerbose,
    ):
        pass
