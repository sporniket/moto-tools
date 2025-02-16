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

from moto_prettier import PrettierCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
)


def mockStdInput(lines):
    return io.StringIO("\n".join(lines) + "\n")


def test_that_it_forces_uppercase_outside_of_string_litterals():
    input_lines = ["10 cls", '20 print "Hello !":print "How are you doing ?"']
    baseArgs = ["prog"]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = PrettierCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 CLS
20 PRINT "Hello !":PRINT "How are you doing ?"
"""
        )


def test_that_it_reads_from_stdin_when_input_file_is_dash():
    input_lines = ["10 cls", '20 print "Hello !":print "How are you doing ?"']
    baseArgs = ["prog", "-"]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = PrettierCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 CLS
20 PRINT "Hello !":PRINT "How are you doing ?"
"""
        )


def test_that_it_processes_specified_file():
    input_lines = ["10 ' NOT THAT ONE"]
    dataFolder = os.path.join(".", "tests", "data")
    baseArgs = ["prog", os.path.join(dataFolder, "in_ugly.bas")]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = PrettierCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 CLS
20 PRINT "Hello !":PRINT "How are you doing ?"
"""
        )


def test_that_it_can_manage_files_and_stdin():
    input_lines = [
        "10 cls",
        '20 print "Hello from stdin !":print "How are you doing ?"',
    ]
    dataFolder = os.path.join(".", "tests", "data")
    baseArgs = [
        "prog",
        os.path.join(dataFolder, "in_ugly.bas"),
        "-",
    ]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = PrettierCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 CLS
20 PRINT "Hello !":PRINT "How are you doing ?"
10 CLS
20 PRINT "Hello from stdin !":PRINT "How are you doing ?"
"""
        )
