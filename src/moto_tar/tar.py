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

from moto_lib.fs_tape import LeaderTapeBlockDescriptor, Tape, TapeBlock, TypeOfTapeBlock
from moto_lib.fs_tape.listeners import (
    TapeImageCliListener,
    TapeImageCliListenerQuiet,
    TapeImageCliListenerVerbose,
)

from moto_lib.fs_tape.image_manager import (
    SingleTapeImageManager,
    TapeImageFromDiskManager,
)
from moto_lib.fs_tape.image_worker import (
    TapeImageContentEnumerator,
    TapeImageContentExtractor,
    TapeImageContentInjector,
)


class TapeArchiveCli:
    @staticmethod
    def createArgParser() -> ArgumentParser:
        parser = ArgumentParser(
            prog="python3 -m moto_tar",
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
            "archive",
            metavar="<archive.k7>",
            type=str,
            help="the designated tape archive",
        )

        parser.add_argument(
            "sources",
            metavar="<source file>",
            type=str,
            nargs="*",
            help="a list of source files",
        )

        commandGroup = parser.add_mutually_exclusive_group(required=True)
        commandGroup.add_argument(
            "-c",
            "--create",
            dest="action",
            action="store_const",
            const="create",
            help=f"Assemble the designated files into the designated tape archive.",
        )
        commandGroup.add_argument(
            "-t",
            "--list",
            dest="action",
            action="store_const",
            const="list",
            help=f"List all the files contained inside the designated tape archive.",
        )
        commandGroup.add_argument(
            "-x",
            "--extract",
            dest="action",
            action="store_const",
            const="extract",
            help=f"Extract all the files contained inside the designated tape archive.",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help=f"When present, each processed files is displayed in a tabulated format.",
        )

        parser.add_argument(
            "--into",
            help="directory where output files will be generated.",
        )
        return parser

    def __init__(self):
        self._imageManagers = {
            # "add": TapeImageFromDiskManager,
            "create": SingleTapeImageManager,
            "extract": TapeImageFromDiskManager,
            "list": TapeImageFromDiskManager,
        }
        self._workers = {
            # "add": TapeImageContentInjector(),
            "create": TapeImageContentInjector(),
            "extract": TapeImageContentExtractor(),
            "list": TapeImageContentEnumerator(),
        }
        pass

    def createListener(self, operation: str, verbose: bool) -> TapeImageCliListener:
        return (
            TapeImageCliListenerVerbose(operation)
            if verbose
            else TapeImageCliListenerQuiet(operation)
        )

    def createImageManager(self, args) -> SingleTapeImageManager:
        if args.action not in self._imageManagers:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")
        return self._imageManagers[args.action](args.archive)

    def run(self) -> int:
        args = TapeArchiveCli.createArgParser().parse_args()
        sources = args.sources

        listener = self.createListener(
            args.action,
            args.verbose,
        )
        imageManager = self.createImageManager(args)

        if args.action not in self._workers:
            raise RuntimeError(f"action.not.implemented.yet:{args.action}")

        return self._workers[args.action].perform(args, imageManager, listener)
