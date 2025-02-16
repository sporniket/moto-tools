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

# from moto_fdar import DiskArchiveCli
from moto_sdar import DiskArchiveCli

from .utils import (
    initializeTmpWorkspace,
    assert_that_source_is_converted_as_expected,
)

# input_archive = "sporny-basic.k7"

source_dir = os.path.join("tests", "data")

SOURCE_ARCHIVE = "10_lsystem_mo5__2023-10-14.sd"


def test_that_it_does_list_files():
    baseArgs = ["prog", "--list", os.path.join(source_dir, SOURCE_ARCHIVE)]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """Side 0
  0000.BAS
  0001.BAS
  0002.BAS
  0003.BAS
  0004.BAS
  0005.BAS
  0006.BAS
  0007.BAS
  0008.BAS
  0009.BAS
  0010.BAS
  0011.BAS
  0012.BAS
  0013.BAS
  0014.BAS
  LSYS.BAS
  0015.BAS
  0016.BAS
  LSYSMO5B.BAS
  LSYSMO5.BAS
  0017.BAS
  0018.BAS
  0019.BAS
  0020.BAS
  0021.BAS
  0022.BAS
  0023.BAS
Side 1
Side 2
Side 3
"""
        )


def test_that_verbose_mode_does_list_files_with_details():
    baseArgs = ["prog", "--list", "--verbose", os.path.join(source_dir, SOURCE_ARCHIVE)]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = DiskArchiveCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """Side 0
  0000    .BAS  BASIC   TOKEN        631 Bytes      1 block 
  0001    .BAS  BASIC   TOKEN       1287 Bytes      1 block 
  0002    .BAS  BASIC   TOKEN       1792 Bytes      1 block 
  0003    .BAS  BASIC   TOKEN       2801 Bytes      2 blocks
  0004    .BAS  BASIC   TOKEN       2911 Bytes      2 blocks
  0005    .BAS  BASIC   TOKEN       3059 Bytes      2 blocks
  0006    .BAS  BASIC   TOKEN       3452 Bytes      2 blocks
  0007    .BAS  BASIC   TOKEN       4324 Bytes      3 blocks
  0008    .BAS  BASIC   TOKEN       4335 Bytes      3 blocks
  0009    .BAS  BASIC   TOKEN       4619 Bytes      3 blocks
  0010    .BAS  BASIC   TOKEN       5168 Bytes      3 blocks
  0011    .BAS  BASIC   TOKEN       6120 Bytes      4 blocks
  0012    .BAS  BASIC   TOKEN       7224 Bytes      4 blocks
  0013    .BAS  BASIC   TOKEN       7455 Bytes      4 blocks
  0014    .BAS  BASIC   TOKEN       7527 Bytes      4 blocks
  LSYS    .BAS  BASIC   ASCII       8684 Bytes      5 blocks
  0015    .BAS  BASIC   TOKEN       7455 Bytes      4 blocks
  0016    .BAS  BASIC   TOKEN       7026 Bytes      4 blocks
  LSYSMO5B.BAS  BASIC   TOKEN       7065 Bytes      4 blocks
  LSYSMO5 .BAS  BASIC   ASCII       8066 Bytes      4 blocks
  0017    .BAS  BASIC   TOKEN       7026 Bytes      4 blocks
  0018    .BAS  BASIC   TOKEN       7032 Bytes      4 blocks
  0019    .BAS  BASIC   TOKEN       7038 Bytes      4 blocks
  0020    .BAS  BASIC   TOKEN       7038 Bytes      4 blocks
  0021    .BAS  BASIC   TOKEN       7018 Bytes      4 blocks
  0022    .BAS  BASIC   TOKEN       7103 Bytes      4 blocks
  0023    .BAS  BASIC   TOKEN       7065 Bytes      4 blocks
27 files, (7 + 88) blocks used (59.4%)
---
Side 1
empty, (0 + 0) blocks used (0.0%)
---
Side 2
empty, (0 + 0) blocks used (0.0%)
---
Side 3
empty, (0 + 0) blocks used (0.0%)
"""
        )
