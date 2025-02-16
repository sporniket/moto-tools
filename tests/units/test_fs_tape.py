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
        b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert but.isValid()
    assert but.type == TypeOfTapeBlock.LEADER
    assert but.length == 16
    assert but.checksum == 0x34
    assert but.body == b"\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00"


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
        b"\x00\x11\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
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
        b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x33"
    )
    assert but.isValid() == False


def test_LeaderTapeBlockDescriptor_can_create_tape_bloc():
    assert (
        LeaderTapeBlockDescriptor("banner", "bas", 0, 0).toTapeBlock().rawData
        == b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )


def test_LeaderTapeBlockDescriptor_can_be_build_from_tape_bloc():
    desc = LeaderTapeBlockDescriptor.buildFromTapeBlock(
        b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert desc.fileName == "BANNER"
    assert desc.fileExtension == "BAS"
    assert desc.fileType == 0
    assert desc.fileMode == 0


def test_TapeBlock_build_from_data():
    assert (
        TapeBlock.buildFromData(
            b"\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00"
        ).rawData
        == b"\x01\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )


def test_Tape_next_block_returns_next_block_until_no_more_bloc():
    tapeData = b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"
    tape = Tape(tapeData)
    assert (
        tape.nextBlock().rawData
        == b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )
    assert tape.nextBlock() is None


def test_Tape_next_block_returns_block_when_there_is_enough_ones_before_3c5a():
    block = Tape(
        b"\x01\x01\x01\x3c\x5a\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    ).nextBlock()
    assert block is not None
    assert (
        block.rawData
        == b"\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
    )


def test_Tape_next_block_returns_nothing_when_there_is_not_enough_ones_before_3c5a():
    assert (
        Tape(
            b"\x01\x01\x3c\x5a\x00\x10\x42\x41\x4e\x4e\x45\x52\x20\x20\x42\x41\x53\x00\x00\x00\x34"
        ).nextBlock()
        is None
    )


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


def test_Tape_next_block_return_257_bytes_of_raw_data_when_length_byte_is_zero():
    block = Tape(
        b"\x20\x20\x42\x41\x53\x00\x00\x00\xc2\x01\x01\x01\x01\x01\x01\x01"
        + b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x3c\x5a\x01\x00\xff\x03\x17"
        + b"\x25\xae\x00\x0a\x93\x20\x41\xc8\x5a\x00\x25\xbb\x00\x14\xff\xa4"
        + b"\x20\x33\x2c\x34\x2c\x34\x00\x25\xc1\x00\x1e\x9d\x00\x25\xd9\x00"
        + b"\x28\xab\x20\x22\x43\x6f\x6e\x6e\x65\x78\x69\x35\x20\x76\x30\x2e"
        + b"\x30\x2e\x30\x22\x00\x25\xf5\x00\x32\xab\x20\x22\x28\x63\x29\x32"
        + b"\x30\x32\x32\x20\x44\x61\x76\x69\x64\x20\x53\x50\x4f\x52\x4e\x22"
        + b"\x00\x26\x15\x00\x3c\xab\x20\x22\x46\x72\x65\x65\x20\x53\x6f\x66"
        + b"\x74\x77\x61\x72\x65\x20\x2d\x2d\x20\x47\x50\x4c\x20\x76\x33\x22"
        + b"\x00\x26\x24\x00\x46\x53\x5a\x42\x4f\x41\x52\x44\x58\xd4\x39\x00"
        + b"\x26\x33\x00\x50\x53\x5a\x42\x4f\x41\x52\x44\x59\xd4\x39\x00\x26"
        + b"\x53\x00\x5a\x53\x5a\x42\x4f\x41\x52\x44\xd4\x53\x5a\x42\x4f\x41"
        + b"\x52\x44\x58\xc9\x53\x5a\x42\x4f\x41\x52\x44\x59\xc8\x31\x00\x26"
        + b"\x6e\x00\x64\x84\x20\x56\x42\x4f\x41\x52\x44\x4f\x43\x43\x55\x50"
        + b"\x28\x53\x5a\x42\x4f\x41\x52\x44\x29\x00\x26\x82\x00\x6e\x81\x20"
        + b"\x49\xd4\x30\x20\xbb\x20\x53\x5a\x42\x4f\x41\x52\x44\x00\x26\x98"
        + b"\x00\x78\x20\x56\x42\x4f\x41\x52\x44\x4f\x43\x43\x55\x50\x28\x49"
        + b"\x29\xd4\x30\x00\x26\xa0\x00\x82\x82\x20\x49\x6d\x01\x01\x01\x01"
    ).nextBlock()
    assert block is not None
    assert len(block.rawData) == 257
