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
from moto_lib import TokenizerContext


def test_TokenizerContext_should_find_the_biggest_convertible_sequence_into_token():
    tokens = {"a": 0x1, "b": 0x2, "ab": 0x3}
    context = TokenizerContext()
    for char in "abc":
        context.append(char, tokens)
    context.commit()
    assert context.doneBuffer == b"\x03c"


def test_TokenizerContext_should_find_the_multiple_token():
    tokens = {"a": 0x1, "b": 0x2, "ab": 0x3}
    context = TokenizerContext()
    for char in "abac":
        context.append(char, tokens)
    context.commit()
    assert context.doneBuffer == b"\x03\x01c"
