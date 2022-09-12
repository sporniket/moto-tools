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
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter, FileType

from typing import List, Union, Optional
from enum import Enum


class TapeArchiveCli:
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m moto_tools_tar",
            description="Assemble, list or extract files into or from a tape archive usable with MO/TO computer emulators.",
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
            metavar="source files",
            type=str,
            nargs="+",
            help="a list of source files",
        )

        commandGroup = parser.add_mutually_exclusive_group(required=True)
        commandGroup.add_argument(
            "--create",
            action="store_true",
            help=f"Assemble the designated files into a tape archive.",
        )
        commandGroup.add_argument(
            "--list",
            action="store_true",
            help=f"List all the files contained inside the designated tape archive.",
        )
        commandGroup.add_argument(
            "--extract",
            action="store_true",
            help=f"Extract all the files contained inside the designated tape archive.",
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help=f"When present, each processed files is displayed in a tabulated format.",
        )

        parser.add_argument(
            "--file",
            action="store",
            type=str,
            required=True,
            help=f"The file name of the tape archive.",
        )
        parser.add_argument(
            "--into",
            action="store",
            type=str,
            required=False,
            help="directory where output files will be generated.",
        )
        return parser

    def __init__(self):
        pass

    def run(self) -> Optional[int]:
        args = TapeArchiveCli.createArgParser().parse_args()

        print(f"Archive file : {args.file}")

        if args.verbose:
            print("Verbose mode")

        print(
            f"action : Creation {args.create} ; Listing {args.list} ; Extraction {args.extract}"
        )

        if args.into:
            print(f"into {args.into}")

        sources = args.sources
        print(f"Given source files : {len(sources)}")
        for s in sources:
            print(f"Processing {s}...")

        print("Done")
