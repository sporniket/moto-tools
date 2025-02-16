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

import sys
import re
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def createArgParser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="python3 -m moto_bas2lst",
        description="Convert an BASIC file saved by MO/TO BASIC into plain text.",
        epilog="""---
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
""",
        formatter_class=RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )

    # Add the arguments
    parser.add_argument(
        "sources",
        metavar="<source file>",
        type=str,
        nargs="*",
        help="a list of BASIC files to convert, MUST have the 'BAS' extension (case insensitive) ;"
        " ASCII listing are indicated with a ',a' after the extension (case insensitive)",
    )

    parser.add_argument(
        "--dos",
        action="store_true",
        help=f"When present, use MS-DOS end of line (CR LF sequence).",
    )

    return parser


class BasicToListingCli:
    def run(self) -> int:
        self.args = args = createArgParser().parse_args()
        endOfLine = bytes([0xD, 0xA]) if args.dos else bytes([0xA])

        for source in args.sources:
            asciiMode = False
            if source[-2:].upper() == ",A":
                source = source[:-2]
                asciiMode = True
            if source[-3:].upper() != "BAS":
                raise ValueError(
                    f"Extension 'BAS' (case insensitive) not found for '{source}'."
                )
            with open(source, "rb") as f:
                data = f.read()
            if asciiMode:
                with open(source[:-3] + "lst", "wb") as lst:
                    lineOfCodeLength = 0
                    for byte in data:
                        if byte in [0xD, 0xA]:
                            if lineOfCodeLength > 0:
                                lst.write(endOfLine)
                            lineOfCodeLength = 0
                        else:
                            lst.write(bytes([byte]))
                            lineOfCodeLength += 1
                    if lineOfCodeLength > 0:
                        lst.write(endOfLine)
        return 0
