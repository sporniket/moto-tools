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
        prog="python3 -m moto_nl",
        description="Number the lines of the given MO/TO BASIC listing, where there are missing line numbers. An already numbered line is left untouched, and is taken into account to number the next line.",
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
        help="a list of source files",
    )

    parser.add_argument(
        "-i",
        "--line-increment",
        metavar="<increment>",
        type=int,
        default=10,
        help=f"When specified, the increment will be added to the number of the current line to number the next line.",
    )

    parser.add_argument(
        "-v",
        "--starting-line-number",
        metavar="<start>",
        type=int,
        default=10,
        help=f"When specified, the first line will be numbered with this number.",
    )

    parser.add_argument(
        "-w",
        "--number-width",
        metavar="<width>",
        type=int,
        default=0,
        help=f"When specified, the number will be padded with spaces to occupy the required width.",
    )
    return parser


class NumberLineCli:
    def run(self) -> int:
        args = createArgParser().parse_args()
        numberLine = args.starting_line_number
        for line in sys.stdin:
            line = line.rstrip("\n")
            match = re.search("^([1-9][0-9]*).*$", line)
            if match is None:
                paddedNumber = f"{numberLine}"
                if len(paddedNumber) < args.number_width:
                    paddedNumber += "".join(
                        [" " for i in range(len(paddedNumber), args.number_width)]
                    )
                print(f"{paddedNumber} {line}")
                numberLine += args.line_increment
            else:
                print(line)
                numberLine = int(match.group(1)) + args.line_increment

        return 0
