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
from moto_lib import Tape, TapeBlock, LeaderTapeBlockDescriptor, TypeOfTapeBlock
import pytest


def test_TapeBlock_with_valid_leader_block():
    but = TapeBlock(
        b"\x00\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert but.isValid()
    assert but.type == TypeOfTapeBlock.LEADER
    assert but.length == 16
    assert but.checksum == 0x34
    assert but.body == b"\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00"


def test_TapeBlock_with_valid_trailer_block():
    but = TapeBlock(b"\xff\x02\x00")
    assert but.isValid()
    assert but.type == TypeOfTapeBlock.EOF
    assert but.length == 2
    assert but.checksum == 0x00
    assert but.body == b""


def test_TapeBlock_with_valid_data_block():
    but = TapeBlock(
        b"\x01\x22\x28\xa4\x01\x36\x20\x82\x20\x4a\x00\x28\xab\x01\x40\x20\xab\x00\x28\xb3\x01\x4a\x82\x20\x49\x00\x28\xb9\x01\x54\x80\x00\x00\x00\x4b"
    )
    assert but.isValid()
    assert but.type == TypeOfTapeBlock.DATA
    assert but.length == 34
    assert but.checksum == 0x4B
    assert (
        but.body
        == b"\x28\xa4\x01\x36\x20\x82\x20\x4a\x00\x28\xab\x01\x40\x20\xab\x00\x28\xb3\x01\x4a\x82\x20\x49\x00\x28\xb9\x01\x54\x80\x00\x00\x00"
    )


def test_TapeBlock_truncated_with_valid_checksum_should_be_invalid():
    but = TapeBlock(
        b"\x00\x11\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert but.isValid() == False


def test_TapeBlock_with_length_1_is_invalid():
    but = TapeBlock(b"\x00\x01\x00")
    assert but.isValidChecksum()
    assert but.isValidLength() == False
    but = TapeBlock(b"\x00\x01")
    assert but.isValidLength() == False
    assert but.isValidChecksum() == False


def test_TapeBlock_with_length_byte_0_is_256_bytes_long():
    but = TapeBlock(b"\x00\x00\x00")
    assert but.length == 256


def test_TapeBlock_with_invalid_checksum_should_be_invalid():
    but = TapeBlock(
        b"\x00\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x33"
    )
    assert but.isValid() == False


def test_LeaderTapeBlockDescriptor_can_create_tape_bloc():
    assert (
        LeaderTapeBlockDescriptor("banner", "bas", 0, 0).toTapeBlock().rawData
        == b"\x00\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )


def test_LeaderTapeBlockDescriptor_can_be_build_from_tape_bloc():
    desc = LeaderTapeBlockDescriptor.buildFromTapeBlock(
        b"\x00\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert desc.fileName == "BANNER"
    assert desc.fileExtension == "BAS"
    assert desc.fileType == 0
    assert desc.fileMode == 0


def test_TapeBlock_build_from_data():
    assert (
        TapeBlock.buildFromData(
            b"\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00"
        ).rawData
        == b"\x01\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )


def test_Tape_next_block_returns_next_block_until_no_more_bloc():
    tapeData = b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"
    tape = Tape(tapeData)
    assert (
        tape.nextBlock().rawData
        == b"\x00\x10\x42\x41\x4E\x4E\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert tape.nextBlock() is None


def test_Tape_next_block_returns_nothing_when_the_end_of_the_tape_happens_before_block_length():
    assert (
        Tape(
            b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a"
        ).nextBlock()
        is None
    )
    assert (
        Tape(
            b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a\x00"
        ).nextBlock()
        is None
    )


def test_Tape_next_block_returns_truncated_block_at_the_end_of_tape():
    block = Tape(
        b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a\x00\x10"
    ).nextBlock()
    assert block is not None
    assert block.rawData == b"\x00\x10"
    assert block.isValid() == False
