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

from moto_nl import NumberLineCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
)

input_archive = "sporny-basic.k7"


def mockStdInput(lines):
    return io.StringIO("\n".join(lines) + "\n")


def test_that_it_does_number_lines():
    input_lines = ["cls", 'Print "Hello"', "locate 10,1"]
    baseArgs = ["prog"]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = NumberLineCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 cls
20 Print "Hello"
30 locate 10,1
"""
        )


def test_that_it_does_take_under_account_already_numbered_lines():
    input_lines = ["cls", '5 Print "Hello"', "locate 10,1"]
    baseArgs = ["prog"]
    with patch.object(sys, "argv", baseArgs):
        with patch.object(sys, "stdin", mockStdInput(input_lines)):
            with redirect_stdout(io.StringIO()) as out:
                returnCode = NumberLineCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 cls
5 Print "Hello"
15 locate 10,1
"""
        )
