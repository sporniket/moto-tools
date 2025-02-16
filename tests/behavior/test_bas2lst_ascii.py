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
from contextlib import redirect_stdout, redirect_stderr

from moto_bas2lst import BasicToListingCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
    initializeTmpWorkspace,
)

source_dir = os.path.join(".", "tests", "data")
source_dir_expected = os.path.join(".", "tests", "data.expected")

source_files = ["B2LIN.BAS"]


def test_that_it_uses_unix_newlines_by_default():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in source_files]
    )
    baseArgs = ["prog"] + [
        os.path.join(tmp_dir, f"{source},a") for source in source_files
    ]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            with redirect_stderr(io.StringIO()) as err:
                returnCode = BasicToListingCli().run()
        assert returnCode == 0
        assert out.getvalue() == ""
        assert err.getvalue() == ""
        for f in source_files:
            pathActual = os.path.join(tmp_dir, f"{f[:-3]}lst")
            assert os.path.exists(pathActual) and os.path.isfile(pathActual)
            assert filecmp.cmp(
                pathActual,
                os.path.join(source_dir_expected, f"{f[:-4]}-unix.lst"),
                shallow=False,
            )
    shutil.rmtree(tmp_dir)


def test_that_it_uses_msdos_newlines_with_dos_switch():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in source_files]
    )
    baseArgs = ["prog", "--dos"] + [
        os.path.join(tmp_dir, f"{source},a") for source in source_files
    ]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            with redirect_stderr(io.StringIO()) as err:
                returnCode = BasicToListingCli().run()
        assert returnCode == 0
        assert out.getvalue() == ""
        assert err.getvalue() == ""
        for f in source_files:
            pathActual = os.path.join(tmp_dir, f"{f[:-3]}lst")
            assert os.path.exists(pathActual) and os.path.isfile(pathActual)
            assert filecmp.cmp(
                pathActual,
                os.path.join(source_dir_expected, f"{f[:-4]}-msdos.lst"),
                shallow=False,
            )
    shutil.rmtree(tmp_dir)


def test_that_it_uses_unix_newlines_by_default():
    files = ["ASC_0D0A.BAS"]
    tmp_dir = initializeTmpWorkspace([os.path.join(source_dir, f) for f in files])
    baseArgs = ["prog"] + [os.path.join(tmp_dir, f"{source},a") for source in files]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            with redirect_stderr(io.StringIO()) as err:
                returnCode = BasicToListingCli().run()
        assert returnCode == 0
        assert out.getvalue() == ""
        assert err.getvalue() == ""
        for f in files:
            pathActual = os.path.join(tmp_dir, f"{f[:-3]}lst")
            assert os.path.exists(pathActual) and os.path.isfile(pathActual)
            assert filecmp.cmp(
                pathActual,
                os.path.join(source_dir_expected, f"{f[:-3]}lst"),
                shallow=False,
            )
    shutil.rmtree(tmp_dir)
