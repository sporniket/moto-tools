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

from .tokenizer import TokenizerContext


basicTokensMap = {
    "END": 0x80,
    "FOR": 0x81,
    "NEXT": 0x82,
    "DATA": 0x83,
    "DIM": 0x84,
    "READ": 0x85,
    "GO": 0x87,
    "RUN": 0x88,
    "IF": 0x89,
    "RESTORE": 0x8A,
    "RETURN": 0x8B,
    "REM": 0x8C,
    "'": 0x8D,
    "STOP": 0x8E,
    "ELSE": 0x8F,
    "TRON": 0x90,
    "TROFF": 0x91,
    "DEFSTR": 0x92,
    "DEFINT": 0x93,
    "DEFSNG": 0x94,
    "ON": 0x96,
    "TUNE": 0x97,
    "ERROR": 0x98,
    "RESUME": 0x99,
    "AUTO": 0x9A,
    "DELETE": 0x9B,
    "LOCATE": 0x9C,
    "CLS": 0x9D,
    "CONSOLE": 0x9E,
    "PSET": 0x9F,
    "MOTOR": 0xA0,
    "SKIPF": 0xA1,
    "EXEC": 0xA2,
    "BEEP": 0xA3,
    "COLOR": 0xA4,
    "LINE": 0xA5,
    "BOX": 0xA6,
    "ATTRB": 0xA8,
    "DEF": 0xA9,
    "POKE": 0xAA,
    "PRINT": 0xAB,
    "CONT": 0xAC,
    "LIST": 0xAD,
    "CLEAR": 0xAE,
    "DOS": 0xAF,
    "NEW": 0xB1,
    "SAVE": 0xB2,
    "LOAD": 0xB3,
    "MERGE": 0xB4,
    "OPEN": 0xB5,
    "CLOSE": 0xB6,
    "INPEN": 0xB7,
    "PEN": 0xB8,
    "PLAY": 0xB9,
    "TAB": 0xBA,
    "TO": 0xBB,
    "SUB": 0xBC,
    "FNC": 0xBD,
    "SPC": 0xBE,
    "USING": 0xBF,
    "USR": 0xC0,
    "ERL": 0xC1,
    "ERR": 0xC2,
    "OFF": 0xC3,
    "THEN": 0xC4,
    "NOT": 0xC5,
    "STEP": 0xC6,
    "+": 0xC7,
    "-": 0xC8,
    "*": 0xC9,
    "/": 0xCA,
    "^": 0xCB,
    "AND": 0xCC,
    "OR": 0xCD,
    "XOR": 0xCE,
    "EQV": 0xCF,
    "IMP": 0xD0,
    "MOD": 0xD1,
    ">": 0xD3,
    "=": 0xD4,
    "<": 0xD5,
    "DSKIN": 0xD6,
    "DSKO$": 0xD7,
    "KILL": 0xD8,
    "NAME": 0xD9,
    "FIELD": 0xDA,
    "LSET": 0xDB,
    "RSET": 0xDC,
    "PUT": 0xDD,
    "GET": 0xDE,
    "VERIFY": 0xDF,
    "DEVICE": 0xE0,
    "DIR": 0xE1,
    "FILES": 0xE2,
    "WRITE": 0xE3,
    "UNLOAD": 0xE4,
    "BACKUP": 0xE5,
    "COPY": 0xE6,
    "CIRCLE": 0xE7,
    "PAINT": 0xE8,
    "DRAW": 0xE9,
    "RENUM": 0xEA,
    "SWAP": 0xEB,
    "SGN": 0xFF80,
    "INT": 0xFF81,
    "APS": 0xFF82,
    "FRE": 0xFF83,
    "SQL": 0xFF84,
    "LOG": 0xFF85,
    "EXP": 0xFF86,
    "COS": 0xFF87,
    "SIN": 0xFF88,
    "TAN": 0xFF89,
    "PEEK": 0xFF8A,
    "LEN": 0xFF8B,
    "STR$": 0xFF8C,
    "VAL": 0xFF8D,
    "ASC": 0xFF8E,
    "CHR$": 0xFF8F,
    "EOF": 0xFF90,
    "CINT": 0xFF91,
    "CSNG": 0xFF92,
    "CDBL": 0xFF93,
    "FIX": 0xFF94,
    "HEX$": 0xFF95,
    "OCT$": 0xFF96,
    "STICK": 0xFF97,
    "STRIG": 0xFF98,
    "GR$": 0xFF99,
    "LEFT$": 0xFF9A,
    "RIGHT$": 0xFF9B,
    "MID$": 0xFF9C,
    "INSTR": 0xFF9D,
    "VARPTR": 0xFF9E,
    "RND": 0xFF9F,
    "INKEY$": 0xFFA0,
    "INPUT": 0xFFA1,
    "CSRLIN": 0xFFA2,
    "POINT": 0xFFA3,
    "SCREEN": 0xFFA4,
    "POS": 0xFFA5,
    "PTRIG": 0xFFA6,
    "DSKF": 0xFFA7,
    "CVI": 0xFFA8,
    "CVS": 0xFFA9,
    "MKI$": 0xFFAB,
    "MKS$": 0xFFAC,
    "LOC": 0xFFAE,
    "LOF": 0xFFAF,
    "SPACE$": 0xFFB0,
    "STRING$": 0xFFB1,
    "DSKI$": 0xFFB2,
}

basicTokensDb = {"map": basicTokensMap, "rules": {"requireColonIfNotBlank": ["ELSE"]}}

litteralTokensDb = {}  # no tokenization in litterals


class ListingToAsciiBasicConverter:
    def convert(self, f, bas):
        endOfLine = bytes([0xD])
        lines = f.readlines()
        lineOfCodeLength = 0
        bas.write(endOfLine)
        for line in lines:
            line = line.rstrip()
            for car in line:
                car = ord(car)
                if car < 0x80:
                    bas.write(bytes([car]))
            bas.write(endOfLine)


class ListingToTokenizedBasicConverter:
    SPECIAL_CHARS = [
        ".",
        ",",
        "(",
        ")",
        ":",
        " ",
    ]

    def toUint16(self, value):
        return bytes([(value // 256) & 0xFF, value & 0xFF])

    def extractLineParts(self, line) -> (int, str):
        match = re.search("^([1-9][0-9]*).*$", line)
        if match is None:
            raise ValueError(f"No line number in this line : '{line}'")
        lineNumber = int(match.group(1))
        line = line[len(match.group(1)) : -1]
        if line[0] == " ":
            line = line[1:]

        return (lineNumber, line)

    def parseLine(self, line, tokenizer):
        isInLiteralString = False
        for char in line:
            charBytes = bytes(char, "utf-8")
            if char == '"':
                tokenizer.commit()
                isInLiteralString = not isInLiteralString
                if isInLiteralString:
                    tokenizer.appendAsLitteral(char)
                else:
                    tokenizer.appendAsToken(char)
                tokenizer.commit()
                continue
            if isInLiteralString:
                tokenizer.appendAsLitteral(char)
                continue
            if char in ListingToTokenizedBasicConverter.SPECIAL_CHARS:
                tokenizer.appendAsToken(char)
                tokenizer.commit()
                continue
            # not in string litteral, convert to uppercase
            char = char.upper()
            charBytes = bytes(char, "utf-8")
            tokenizer.appendAsToken(char)

    def convert(self, f, bas):
        lines = f.readlines()
        header = bytearray()
        body = bytearray()
        pointerNext = 0x25A4
        zeroUint8 = bytes([0])
        zeroUint16 = bytes([0, 0])

        # convert source line by line
        tokenizer = TokenizerContext(basicTokensDb, litteralTokensDb)
        for line in lines:
            tokenizer.reset()
            # 1 -- extract the line number and the first space after
            (lineNumber, line) = self.extractLineParts(line)

            # 2 -- parse the line
            self.parseLine(line, tokenizer)

            tokenizer.commit()
            lineBuffer = tokenizer.doneBuffer
            lineBuffer += zeroUint8
            pointerNext += len(lineBuffer) + 4
            body += self.toUint16(pointerNext)
            body += self.toUint16(lineNumber)
            body += lineBuffer

        # build header
        body += zeroUint16
        bodyLength = len(body)
        header += bytes([0xFF])
        header += self.toUint16(bodyLength)

        # write to file
        bas.write(header)
        bas.write(body)
