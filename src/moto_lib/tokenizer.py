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

from enum import Enum
from typing import List


def toUint8(value):
    return bytes([value & 0xFF])


def toUint16(value):
    return bytes([(value // 256) & 0xFF, value & 0xFF])


def bytesFromUint(value):
    return toUint8(value) if value < 256 else toUint16(value)


class TokenizerContext:
    def __init__(self, databaseOfTokens, databaseOfLitteral):
        self.reset()
        self._tokens = databaseOfTokens["map"]
        self._requireColonIfNotBlank = databaseOfTokens["rules"][
            "requireColonIfNotBlank"
        ]
        self._litteral = databaseOfLitteral

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

    def appendAsToken(self, inputSeq):
        tmpBucket = self.bucket + inputSeq
        self.sourceSequence += inputSeq
        if self.sourceSequence in self._tokens:
            # found biggest sequence convertible
            if self.sourceSequence in self._requireColonIfNotBlank:
                self.candidateBuffer = toUint8(0x3A) + bytesFromUint(
                    self._tokens[self.sourceSequence]
                )
            else:
                self.candidateBuffer = bytesFromUint(self._tokens[self.sourceSequence])
            self.bucket = ""
        elif self.bucket in self._tokens:
            # found an early tokenizable sequence
            if self.sourceSequence in self._requireColonIfNotBlank:
                self.candidateBuffer = toUint8(0x3A) + bytesFromUint(
                    self._tokens[self.bucket]
                )
            else:
                self.candidateBuffer = bytesFromUint(self._tokens[self.bucket])
            self.bucket = ""
        elif inputSeq in self._tokens:
            # found a token on the spot
            self.commit()
            self.candidateBuffer += bytesFromUint(self._tokens[inputSeq])
            self.commit()
        else:
            self.bucket += inputSeq

    def appendAsLitteral(self, inputSeq):
        tmpBucket = self.bucket + inputSeq
        self.sourceSequence += inputSeq
        if self.sourceSequence in self._litteral:
            # found biggest sequence convertible
            self.candidateBuffer = bytesFromUint(self._litteral[self.sourceSequence])
            self.bucket = ""
        elif self.bucket in self._litteral:
            # found an early tokenizable sequence
            self.candidateBuffer += bytesFromUint(self._litteral[self.bucket])
            self.bucket = ""
        elif inputSeq in self._litteral:
            # found a token on the spot
            self.commit()
            self.candidateBuffer += bytesFromUint(self._litteral[inputSeq])
            self.commit()
        else:
            self.bucket += inputSeq

    def isBlank(self):
        """Assess whether the done buffer so far is only full of spaces, or empty."""
        for x in self.doneBuffer:
            if x != 0x20:
                return False
        return True


class TokenizerPhase(Enum):
    """
    Distinguish phases when the tokenizer CAN tokenize, and phases when it CANNOT.
    """

    DO_TOKENIZE = 0
    WAIT_NEXT_STATEMENT = 1


class TokenizerPhaseAutomaton:
    """
    Automaton tasked with assessing when the tokenizer can tokenize, and when it cannot.
    """

    def __init__(
        self, matchersForWaitNextStatement: List[str], matchersForDoTokenize: List[str]
    ):
        """
        Initialize the automaton to an initial state, and setup the matchers

        Args:
            matchersForWaitNextStatement (List[str]): after those sequences, the automaton will assess that the tokenizer CANNOT parse.
            matchersForDoTokenize (List[str]): after those sequences, the automaton will assess that the tokenizer CAN parse.
        """
        self.phase = TokenizerPhase.DO_TOKENIZE
        self.matchersForWaitNextStatement = matchersForWaitNextStatement
        self.matchersForDoTokenize = matchersForDoTokenize

    def update(self, context: TokenizerContext, lastChar: str) -> bool:
        """
        Update the automaton state, return True if state changed

        Args:
            context (TokenizerContext): the current tokenizer context
            lastChar (str): the last char appended to the context

        Returns:
            bool: True if the state of automaton changed, False otherwise.
        """
        if self.phase == TokenizerPhase.DO_TOKENIZE:
            if (
                context.sourceSequence in self.matchersForWaitNextStatement
                or context.bucket in self.matchersForWaitNextStatement
            ):
                self.phase = TokenizerPhase.WAIT_NEXT_STATEMENT
                return True
        else:  # self.phase == TokenizerPhase.WAIT_NEXT_STATEMENT
            if lastChar in self.matchersForDoTokenize:
                self.phase = TokenizerPhase.DO_TOKENIZE
                return True
        return False
