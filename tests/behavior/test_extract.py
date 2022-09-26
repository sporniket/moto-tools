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
import os
import shutil
import time
import sys
import io
from typing import List, Union, Optional

from unittest.mock import patch
from contextlib import redirect_stdout

from moto_tar import TapeArchiveCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
)

input_archive = "sporny-basic.k7"


def test_that_extract_command_does_extract_files():
    source_dir = os.path.join(".", "tests", "data")
    baseArgs = ["prog", "-x", os.path.join(source_dir, input_archive)]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            TapeArchiveCli().run()
        assert (
            out.getvalue()
            == """Archive : ./tests/data/sporny-basic.k7
Given source files : 0
Listing...
BANNER.BAS
BANNER2.BAS
C5000.BAS
C5001.BAS
C5001LST.BAS
C5002.BAS
Done
"""
        )


def test_that_verbose_list_command_does_list_files_with_details():
    source_dir = os.path.join(".", "tests", "data")
    baseArgs = ["prog", "-xv", os.path.join(source_dir, input_archive)]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            TapeArchiveCli().run()
        assert (
            out.getvalue()
            == """Archive : ./tests/data/sporny-basic.k7
Verbose mode
Given source files : 0
Listing...
BANNER.BAS\t0\t0\t0\t#3\t102 octets\t1 blocks.
BANNER2.BAS\t0\t0\t0\t#6\t102 octets\t1 blocks.
C5000.BAS\t0\t0\t0\t#12\t794 octets\t4 blocks.
C5001.BAS\t0\t0\t0\t#18\t804 octets\t4 blocks.
C5001LST.BAS\t0\t65535\t0\t#24\t942 octets\t4 blocks.
C5002.BAS\t0\t0\t0\t#30\t836 octets\t4 blocks.
Done
"""
        )