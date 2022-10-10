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
        prog="python3 -m moto_lst2bas",
        description="Convert a plain text file into a BASIC file loadable by MO/TO BASIC.",
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
        help="a list of plain text files to convert, MUST have the 'lst' extension (case insensitive) ;"
        " to convert into an ASCII listing, append a ',a' after the extension (case insensitive)",
    )

    return parser


class ListingToBasicCli:
    def run(self) -> int:
        self.args = args = createArgParser().parse_args()
        endOfLine = bytes([0xD])

        for source in args.sources:
            asciiMode = False
            if source[-2:].upper() == ",A":
                source = source[:-2]
                asciiMode = True
            if source[-3:].upper() != "LST":
                raise ValueError(
                    f"Extension 'lst' (case insensitive) not found for '{source}'."
                )
            with open(source, "rt") as f:
                lines = f.readlines()
            if asciiMode:
                with open(source[:-3] + "bas", "wb") as bas:
                    lineOfCodeLength = 0
                    bas.write(endOfLine)
                    for line in lines:
                        line = line.rstrip()
                        for car in line:
                            car = ord(car)
                            if car < 0x80:
                                bas.write(bytes([car]))
                        bas.write(endOfLine)
        return 0
