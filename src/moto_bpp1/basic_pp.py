import re
import sys


class Basic1PrettyPrinter:
    def __init__(self):
        self.defaultLineNumber = 10

    def processCase(self):
        line = self.resultLine
        groups = re.split('([^"]+)', line)
        dquote_depth = 0
        result = ""
        for group in groups:
            if group == '"':
                dquote_depth = (dquote_depth + 1) & 0x1
            result += group.upper() if dquote_depth == 0 else group
        self.resultLine = result
        return self

    def processNumbering(self):
        line = self.resultLine
        match = re.search("^([1-9][0-9]*).*$", line)
        if match is None:
            self.resultLine = f"{self.defaultLineNumber} {line}"
            self.defaultLineNumber += 10
        else:
            self.defaultLineNumber = int(match.group(1)) + 10

        return self

    def makePretty(self, line: str) -> str:
        self.inputLine = line
        self.resultLine = line
        for processor in [self.processCase, self.processNumbering]:
            processor()
        return self.resultLine
