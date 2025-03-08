"""
---
(c) 2022~2024 David SPORN
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

from enum import Enum

# Python < 3.12 forbids f-strings like `f"{"what" if condition else "ever"}"`
FINAL_S = "s"
FINAL_SPACE = " "
FINAL_NONE = ""
PADDING_8 = "        "
PADDING_22 = "                      "
VERB_READ = "read"
VERB_WRITTEN = "written"


class TypeOfDiskImageProcessing(Enum):
    LISTING = 0
    EXTRACTING = 1  # for extracting files from an image
    UPDATING = 2  # for putting files into an image
