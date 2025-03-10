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

from .tape import Tape


class SingleTapeImageManager:
    def __init__(self, filePath: str):
        self._filePath = filePath
        self.prepareImage()

    def prepareImage(self):
        """Override this method to get your image from somewhere.

        This implementation create a tape image from nothingness.
        """
        self._image = Tape()

    @property
    def image(self) -> Tape:
        return self._image

    def save(self):
        with open(self._filePath, "wb") as f:
            f.write(self._image.rawData)


class TapeImageFromDiskManager(SingleTapeImageManager):
    def prepareImage(self):
        with open(self._filePath, "rb") as f:
            self._image = Tape(f.read())
