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

import filecmp
import os
import shutil
import sys
import time

from typing import List
from unittest.mock import patch


def makeTmpDirOrDie(suffix: str = None) -> str:
    newdir = os.path.join(".", f"tmp.test_{suffix}" if suffix != None else "tmp")
    if os.path.exists(newdir):
        if os.path.isdir(newdir):
            return newdir
        raise (ResourceWarning(f"{newdir} is not a directory"))
    os.mkdir(newdir)
    return newdir


def initializeTmpWorkspace(files: List[str]) -> str:
    tmp_dir = makeTmpDirOrDie(time.time())
    for file in files:
        if file[-2:].upper() == ",A":
            file = file[:-2]
        shutil.copy(file, tmp_dir)
    return tmp_dir


def assert_that_source_is_converted_as_expected(pathActual: str, pathExpected: str):
    assert filecmp.cmp(pathActual, pathExpected, shallow=False)
