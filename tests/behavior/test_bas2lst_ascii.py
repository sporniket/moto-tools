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

from moto_bas2lst import BasicToListingCli

from .utils import (
    makeTmpDirOrDie,
    assert_that_source_is_converted_as_expected,
    initializeTmpWorkspace,
)

source_dir = os.path.join(".", "tests", "data")

source_files = ["B2LIN.BAS,a"]


def test_that_it_uses_unix_newlines_by_default():
    tmp_dir = initializeTmpWorkspace(
        [os.path.join(source_dir, f) for f in source_files]
    )
    baseArgs = ["prog", os.path.join(source_dir, "B2LIN.BAS,a")]
    with patch.object(sys, "argv", baseArgs):
        with redirect_stdout(io.StringIO()) as out:
            returnCode = BasicToListingCli().run()
        assert returnCode == 0
        assert (
            out.getvalue()
            == """10 DEFINT A-Z
20 SCREEN 3,4,4
30 CLS
35 ATTRB 0,1:LOCATE 0,1
40 PRINT "Connexi5 v0.0.0"
45 ATTRB 0,0:LOCATE 0,2
50 PRINT "(c)2022 David SPORN"
60 PRINT "Free Software -- GPL v3"
70 SZBOARDX=9
80 SZBOARDY=9
90 SZBOARD=SZBOARDX*SZBOARDY-1
100 DIM VBOARDOCCUP(SZBOARD)
110 FOR I=0 TO SZBOARD
120  VBOARDOCCUP(I)=0
130 NEXT I
140 LBBOARDHEADER$=" ABCDEFGHI"
150 LBBOARDROWS$="123456789"
160 CLRPEN=0
170 CLRPAPER=15
180 COLOR CLRPEN,CLRPAPER
190 PRINT LBBOARDHEADER$
200 NDXCELL=0
210 FOR I=0 TO SZBOARDY-1
220  PRINT MID$(LBBOARDROWS$,I+1,1);
230  FOR J=0 TO SZBOARDX-1
240   VLCELL=VBOARDOCCUP(NDXCELL)
250   IF VLCELL=2 THEN CLRPAPER=4
260   IF VLCELL=1 THEN CLRPAPER=1
270   IF VLCELL=0 THEN CLRPAPER=15
280   IF CLRPAPER=15 THEN CLRPEN=0 ELSE CLRPEN=7
290   IF NDXCELL=20 OR NDXCELL=24 OR NDXCELL=40 OR NDXCELL=56 OR NDXCELL=60 THEN PRINT "#"; ELSE PRINT "+";
300   NDXCELL=NDXCELL+1
310  NEXT J
320  PRINT
330 NEXT I
340 COLOR 3,4
350 END
"""
        )
