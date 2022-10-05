import sys
import re

__all__ = ["NumberLineCli"]


class NumberLineCli:
    def run(self) -> int:
        numberLine = 10
        for line in sys.stdin:
            line = line.rstrip("\n")
            match = re.search("^([1-9][0-9]*).*$", line)
            if match is None:
                print(f"{numberLine} {line}")
                numberLine += 10
            else:
                print(line)
                numberLine = int(match.group(1)) + 10

        return 0
