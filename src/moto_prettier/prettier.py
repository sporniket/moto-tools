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

import re
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def createArgParser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="python3 -m moto_prettier",
        description="Make the given text into a good looking MO/TO basic source.",
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
        help="a list of source files. one or more files to process ; "
        "a dash `-` designate the standard input. "
        "Without any file, it will also use the standard input as source. ",
    )

    return parser


class PrettierCli:
    def processLine(self, line: str):
        args = self.args
        line = line.rstrip("\n")
        groups = re.split('([^"])', line)
        dquote_depth = 0
        result = ""
        for group in groups:
            if group == '"':
                dquote_depth = (dquote_depth + 1) & 0x1
            result += group.upper() if dquote_depth == 0 else group
        print(result)

    def run(self) -> int:
        self.args = args = createArgParser().parse_args()
        if len(args.sources) > 0:
            for source in args.sources:
                if source == "-":
                    for line in sys.stdin:
                        self.processLine(line)
                else:
                    with open(source, "rt") as f:
                        lines = f.readlines()
                    for line in lines:
                        self.processLine(line)
        else:
            for line in sys.stdin:
                self.processLine(line)

        return 0
