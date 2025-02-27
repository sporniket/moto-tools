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

from .image import DiskImage, TypeOfDiskImage


class SingleDiskImageManager:
    """Base class that deals with how to get a DiskImage to work on and how to save it.

    As a default implementation, it creates a DiskImage in memory, with unknown content.

    Lifecycle
    =========

    ```python
    dip = DiskImageProvider(typeOfDiskImage, filePath)

    #... do stuff
    doStuff(dip.image,...)

    #... done, and ok to save
    dip.save()

    ```

    """

    def __init__(self, typeOfDiskImage: TypeOfDiskImage, filePath: str) -> DiskImage:
        self._typeOfDiskImage = typeOfDiskImage
        self._filePath = filePath
        self.prepareImage()

    def prepareImage(self):
        """Override this method to get your image from somewhere.

        This implementation create a disk image from nothingness.
        """
        self._image = DiskImage(bytes(), typeOfDiskImage=self._typeOfDiskImage)

    @property
    def image(self) -> DiskImage:
        return self._image

    def save(self):
        with open(self._filePath, "wb") as f:
            for s in self._image.sides:
                for t in s.tracks:
                    for sector in t.sectors:
                        f.write(sector.dataOfSector)


class DiskImageFromDiskManager(SingleDiskImageManager):
    def prepareImage(self):
        with open(self._filePath, "rb") as f:
            self._image = DiskImage(f.read(), typeOfDiskImage=self._typeOfDiskImage)
