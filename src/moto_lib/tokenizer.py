"""
Tokenizer engine
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


def toUint8(value):
    return bytes([value & 0xFF])


def toUint16(value):
    return bytes([(value // 256) & 0xFF, value & 0xFF])


def bytesFromUint(value):
    return toUint8(value) if value < 256 else toUint16(value)


class TokenizerContext:
    def __init__(self):
        self.reset()

    def reset(self):
        self.doneBuffer = bytearray()
        self.candidateBuffer = bytearray()
        self.sourceSequence = ""
        self.bucket = ""

    def commit(self):
        if len(self.candidateBuffer) > 0:
            self.doneBuffer += self.candidateBuffer
        if len(self.bucket) > 0:
            self.doneBuffer += bytes(self.bucket, "utf-8")
        self.candidateBuffer = bytearray()
        self.sourceSequence = ""
        self.bucket = ""

    def append(self, inputSeq, registryOfTokens):
        self.bucket += inputSeq
        self.sourceSequence += inputSeq
        if self.sourceSequence in registryOfTokens:
            # found biggest sequence convertible
            self.candidateBuffer = bytesFromUint(registryOfTokens[self.sourceSequence])
            self.bucket = ""
        elif self.bucket in registryOfTokens:
            # found an early tokenizable sequence
            self.candidateBuffer += bytesFromUint(registryOfTokens[self.bucket])
            self.bucket = ""
