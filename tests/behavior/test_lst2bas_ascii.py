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
import time
import sys
import io
from typing import List, Union, Optional

from unittest.mock import patch
from contextlib import redirect_stdout

from moto_lst2bas import ListingToBasicCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
    initializeTmpWorkspace,
)

source_dir = os.path.join(".", "tests", "data")
source_dir_expected = os.path.join(".", "tests", "data.expected")

source_files = ["l2bin.lst"]


def test_that_it_convert_plain_text_to_ascii_basic():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in source_files]
    )
    baseArgs = ["prog"] + [
        os.path.join(tmp_dir, f"{source},a") for source in source_files
    ]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = ListingToBasicCli().run()
        assert returnCode == 0
        assert out.getvalue() == ""
        for f in source_files:
            pathActual = os.path.join(tmp_dir, f"{f[:-3]}bas")
            assert os.path.exists(pathActual) and os.path.isfile(pathActual)
            assert filecmp.cmp(
                pathActual,
                os.path.join(source_dir_expected, f"{f[:-4]}-ascii.bas"),
                shallow=False,
            )
    shutil.rmtree(tmp_dir)
