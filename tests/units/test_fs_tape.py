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
from moto_lib.fs_tape import TapeBloc, LeaderTapeBlocDescriptor
import pytest


def test_tape_bloc_with_valid_checksum_should_be_valid():
    but = TapeBloc(
        bytes(
            [
                0x00,
                0x10,
                0x42,
                0x41,
                0x4E,
                0x4E,
                0x45,
                0x52,
                0x20,
                0x20,
                0x42,
                0x41,
                0x53,
                0x00,
                0x00,
                0x00,
                0x34,
            ]
        )
    )
    assert but.isValid() == True


def test_tape_bloc_with_invalid_checksum_should_be_invalid():
    but = TapeBloc(
        bytes(
            [
                0x00,
                0x10,
                0x42,
                0x41,
                0x4E,
                0x4E,
                0x45,
                0x52,
                0x20,
                0x20,
                0x42,
                0x41,
                0x53,
                0x00,
                0x00,
                0x00,
                0x33,
            ]
        )
    )
    assert but.isValid() == False


def test_leader_tape_bloc_descriptor_can_create_tape_bloc():
    assert LeaderTapeBlocDescriptor(
        "banner", "bas", 0, 0
    ).toTapeBloc().rawData == bytes(
        [
            0x00,
            0x10,
            0x42,
            0x41,
            0x4E,
            0x4E,
            0x45,
            0x52,
            0x20,
            0x20,
            0x42,
            0x41,
            0x53,
            0x00,
            0x00,
            0x00,
            0x34,
        ]
    )


def test_tape_bloc_build_from_data():
    assert TapeBloc.buildFromData(
        bytes(
            [
                0x42,
                0x41,
                0x4E,
                0x4E,
                0x45,
                0x52,
                0x20,
                0x20,
                0x42,
                0x41,
                0x53,
                0x00,
                0x00,
                0x00,
            ]
        )
    ).rawData == bytes(
        [
            0x01,
            0x10,
            0x42,
            0x41,
            0x4E,
            0x4E,
            0x45,
            0x52,
            0x20,
            0x20,
            0x42,
            0x41,
            0x53,
            0x00,
            0x00,
            0x00,
            0x34,
        ]
    )
