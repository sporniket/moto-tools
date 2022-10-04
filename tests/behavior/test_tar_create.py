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

from moto_tar import TapeArchiveCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
    initializeTmpWorkspace,
)

source_dir = os.path.join(".", "tests", "data")

source_files = [
    "BANNER.BAS",
    "BANNER2.BAS",
    "C5000.BAS",
    "C5001.BAS",
    "C5001LST.BAS,a",
    "C5002.BAS",
]

output_archive = "mo5.k7"

reference_archive = "sporny-basic.k7"


def test_that_create_command_does_create_tape_archive():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in source_files]
    )
    baseArgs = ["prog", "-c", os.path.join(tmp_dir, output_archive)] + [
        os.path.join(tmp_dir, f) for f in source_files
    ]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            TapeArchiveCli().run()
        pathActual = os.path.join(tmp_dir, output_archive)
        assert os.path.exists(pathActual) and os.path.isfile(pathActual)
        assert filecmp.cmp(
            pathActual, os.path.join(source_dir, reference_archive), shallow=False
        )
    shutil.rmtree(tmp_dir)


def test_that_create_command_fails_when_there_is_too_much_data():

    bigSourceFile = "big_18k.txt"
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in [bigSourceFile]]
    )
    baseArgs = [
        "prog",
        "-c",
        os.path.join(tmp_dir, output_archive),
        os.path.join(tmp_dir, bigSourceFile),
    ]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = TapeArchiveCli().run()
        assert returnCode == 1
        assert (
            out.getvalue()
            == f"""Archive : {os.path.join(tmp_dir, output_archive)}
Given source files : 1
Creating...
Too much data, abort creation.
"""
        )
        pathActual = os.path.join(tmp_dir, output_archive)
        assert not os.path.exists(pathActual)
    shutil.rmtree(tmp_dir)
