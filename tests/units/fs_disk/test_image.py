"""
@Since v0.0.4
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

import pytest

from moto_lib.fs_disk.image import (
    TypeOfDiskImage,
    DiskSector,
    DiskTrack,
    DiskSide,
    DiskImage,
)


######################################################## Test suite for TypeOfDiskImage


def test_TypeOfDiskImage_should_verify_expectations():
    then_TypeOfDiskImage_verify_expectations(
        TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE, 0, 256, 256
    )
    then_TypeOfDiskImage_verify_expectations(
        TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE, 1, 512, 256
    )


def then_TypeOfDiskImage_verify_expectations(
    typeOfImage: TypeOfDiskImage, intValue: int, sizeOfSector: int, sizeOfPayload: int
):
    assert TypeOfDiskImage.fromInt(intValue) == typeOfImage
    assert typeOfImage.sizeOfSector() == sizeOfSector
    assert typeOfImage.sizeOfPayload() == sizeOfPayload


######################################################## Test suite for DiskSector

# --- for emulator images


def test_DiskSector_for_emulator_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskSector([i for i in range(255)])


def test_DiskSector_for_emulator_should_contain_provided_data():
    ds = DiskSector([i for i in range(256)])

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == i

    # verify physical data
    assert len(ds.dataOfSector) == 256
    for i, d in enumerate(ds.dataOfSector):
        assert d == i


def test_DiskSector_for_emulator_should_consume_256_bytes_only_from_data():
    ds = DiskSector([i % 256 for i in range(257)])

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == i

    # verify physical data
    assert len(ds.dataOfSector) == 256
    for i, d in enumerate(ds.dataOfSector):
        assert d == i


def test_DiskSector_for_emulator_should_contain_blank_data_when_no_data_is_provided():
    ds = DiskSector()

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == 0xE5

    # verify physical data
    assert len(ds.dataOfSector) == 256
    for i, d in enumerate(ds.dataOfSector):
        assert d == 0xE5


# --- for SDDrive images


def test_DiskSector_for_sddrive_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskSector(
            [i % 256 for i in range(511)],
            typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
        )


def test_DiskSector_for_sddrive_should_contain_provided_data():
    ds = DiskSector(
        [i % 256 for i in range(512)],
        typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
    )

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == i

    # verify physical data
    assert len(ds.dataOfSector) == 512
    for i, d in enumerate(ds.dataOfSector):
        assert d == i if i < 256 else d == 0xFF


def test_DiskSector_for_sddrive_should_consume_512_bytes_only_from_data():
    ds = DiskSector(
        [i % 256 for i in range(513)],
        typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
    )

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == i

    # verify physical data
    assert len(ds.dataOfSector) == 512
    for i, d in enumerate(ds.dataOfSector):
        assert d == i if i < 256 else d == 0xFF


def test_DiskSector_for_sddrive_should_contain_blank_data_when_no_data_is_provided():
    ds = DiskSector(typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)

    # verify payload
    assert len(ds.dataOfPayload) == 256
    for i, d in enumerate(ds.dataOfPayload):
        assert d == 0xE5

    # verify physical data
    assert len(ds.dataOfSector) == 512
    for i, d in enumerate(ds.dataOfSector):
        assert d == 0xE5 if i < 256 else d == 0xFF


######################################################## Utilities for subsequent test suites

BLANK_SECTOR = bytes([0xE5 for d in range(256)])


def then_DiskSector_dataOfPayload_has_expected_content(
    sector: DiskSector, data: bytes or bytearray
):
    payload = sector.dataOfPayload
    sizeOfPayload = len(payload)
    assert sizeOfPayload == len(data)
    for i in range(sizeOfPayload):
        assert payload[i] == data[i]
    data = sector.dataOfSector
    sizeOfData = len(data)
    if sizeOfData > sizeOfPayload:
        # SDDrive image
        for i in range(sizeOfPayload, sizeOfData):
            assert data[i] == 0xFF


######################################################## Test suite for DiskTrack


# --- for emulator images


def test_DiskTrack_for_emulator_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskTrack([0 for i in range(4095)])


def test_DiskTrack_for_emulator_should_contain_provided_data():
    source = bytes(
        [dat for s in [[i + 1 for d in range(256)] for i in range(16)] for dat in s]
    )
    track = DiskTrack(source)
    for i, s in enumerate(track.sectors):
        then_DiskSector_dataOfPayload_has_expected_content(
            s, bytes([i + 1 for d in range(256)])
        )


def test_DiskTrack_for_emulator_should_contain_blank_data_when_no_data_is_provided():
    track = DiskTrack()
    for i, s in enumerate(track.sectors):
        then_DiskSector_dataOfPayload_has_expected_content(s, BLANK_SECTOR)


# --- for SDDrive images


def test_DiskTrack_for_sddrive_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskTrack(
            [0 for i in range(8191)],
            typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
        )


def test_DiskTrack_for_sddrive_should_contain_provided_data():
    source = bytes(
        [dat for s in [[i + 1 for d in range(512)] for i in range(16)] for dat in s]
    )
    track = DiskTrack(source, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    for i, s in enumerate(track.sectors):
        then_DiskSector_dataOfPayload_has_expected_content(
            s, bytes([i + 1 for d in range(256)])
        )


def test_DiskTrack_for_sddrive_should_contain_blank_data_when_no_data_is_provided():
    track = DiskTrack(typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    for i, s in enumerate(track.sectors):
        then_DiskSector_dataOfPayload_has_expected_content(s, BLANK_SECTOR)


######################################################## Test suite for DiskSide


# --- for emulator images


def test_DiskSide_for_emulator_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskSide([0 for i in range(327679)])


def test_DiskSide_for_emulator_should_contain_provided_data():
    source = bytes(
        [dat for s in [[i + 1 for d in range(4096)] for i in range(80)] for dat in s]
    )
    side = DiskSide(source)
    for i, t in enumerate(side.tracks):
        expectedPayload = [i + 1 for d in range(256)]
        for s in t.sectors:
            then_DiskSector_dataOfPayload_has_expected_content(s, expectedPayload)


def test_DiskSide_for_emulator_should_contain_blank_data_when_no_data_is_provided():
    side = DiskSide()
    for i, t in enumerate(side.tracks):
        for s in t.sectors:
            then_DiskSector_dataOfPayload_has_expected_content(s, BLANK_SECTOR)


# --- for SDDrive images


def test_DiskSide_for_sddrive_should_reject_undersized_data():
    with pytest.raises(ValueError) as error:
        DiskSide(
            [0 for i in range(655359)],
            typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
        )


def test_DiskSide_for_sddrive_should_contain_provided_data():
    source = bytes(
        [dat for s in [[i + 1 for d in range(8192)] for i in range(80)] for dat in s]
    )
    side = DiskSide(source, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    for i, t in enumerate(side.tracks):
        expectedPayload = [i + 1 for d in range(256)]
        for s in t.sectors:
            then_DiskSector_dataOfPayload_has_expected_content(s, expectedPayload)


def test_DiskSide_for_sddrive_should_contain_blank_data_when_no_data_is_provided():
    side = DiskSide(typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    for i, t in enumerate(side.tracks):
        for s in t.sectors:
            then_DiskSector_dataOfPayload_has_expected_content(s, BLANK_SECTOR)


######################################################## Test suite for DiskImage


# --- utilities


def then_image_contains_blank_data(image: DiskImage):
    for i, side in enumerate(image.sides):
        for t in side.tracks:
            for sector in t.sectors:
                then_DiskSector_dataOfPayload_has_expected_content(sector, BLANK_SECTOR)


def then_image_contains_test_data(image: DiskImage):
    for i, side in enumerate(image.sides):
        expectedPayload = [i + 1 for d in range(256)]
        for t in side.tracks:
            for sector in t.sectors:
                then_DiskSector_dataOfPayload_has_expected_content(
                    sector, expectedPayload
                )


def createTestDataForDiskImage(numberOfSides: int, bytesPerSide: int) -> bytes:
    return bytes(
        [
            dat
            for s in [
                [i + 1 for d in range(bytesPerSide)] for i in range(numberOfSides)
            ]
            for dat in s
        ]
    )


def createTestDataForEmulator(numberOfSides: int) -> bytes:
    return createTestDataForDiskImage(numberOfSides, 327680)


def createTestDataForSddrive(numberOfSides: int) -> bytes:
    return createTestDataForDiskImage(numberOfSides, 655360)


# --- for emulator images


def test_DiskImage_for_emulator_should_reject_undersized_data():
    ## image with one side - 1 byte
    with pytest.raises(ValueError) as error:
        DiskImage([0 for i in range(327679)])
    ## image with two sides - 1 byte
    with pytest.raises(ValueError) as error:
        DiskImage([0 for i in range(655359)])
    ## image with four sides - 1 byte
    with pytest.raises(ValueError) as error:
        DiskImage([0 for i in range(1310719)])


def test_DiskImage_for_emulator_should_reject_data_for_3_sides_only():
    ## image with three sides
    with pytest.raises(ValueError) as error:
        DiskImage([0 for i in range(983040)])


def test_DiskImage_for_emulator_should_contain_expected_number_of_sides_with_provided_data():
    for numberOfSides in [1, 2, 4]:
        source = createTestDataForEmulator(numberOfSides)
        image = DiskImage(source)
        assert len(image.sides) == numberOfSides
        then_image_contains_test_data(image)


def test_DiskImage_for_emulator_should_contain_at_most_4_disk_sides():
    source = createTestDataForEmulator(5)
    image = DiskImage(source)
    assert len(image.sides) == 4
    then_image_contains_test_data(image)


def test_DiskImage_for_emulator_should_contain_wanted_number_of_sides_with_blank_data_when_no_data_is_provided():
    for numberOfSides in [1, 2, 4]:
        image = DiskImage(wantedNumberOfSides=numberOfSides)
        assert len(image.sides) == numberOfSides
        then_image_contains_blank_data(image)


def test_DiskImage_for_emulator_should_refuse_creating_blank_image_with_only_3_sides():
    with pytest.raises(ValueError) as error:
        DiskImage(wantedNumberOfSides=3)


def test_DiskImage_for_emulator_should_create_blank_image_with_4_sides_when_unspecified_or_more_than_4_is_wanted():
    image = DiskImage()
    assert len(image.sides) == 4
    then_image_contains_blank_data(image)

    image = DiskImage(wantedNumberOfSides=5)
    assert len(image.sides) == 4
    then_image_contains_blank_data(image)


# --- for SDDrive images


def test_DiskImage_for_sddrive_should_reject_undersized_data():
    ## image with four sides - 1 byte
    with pytest.raises(ValueError) as error:
        DiskImage(
            [0 for i in range(2621439)],
            typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
        )


def test_DiskImage_for_sddrive_should_contain_expected_number_of_sides_with_provided_data():
    source = createTestDataForSddrive(4)
    image = DiskImage(source, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    assert len(image.sides) == 4
    then_image_contains_test_data(image)


def test_DiskImage_for_sddrive_should_contain_at_most_4_disk_sides():
    source = createTestDataForSddrive(5)
    image = DiskImage(source, typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    assert len(image.sides) == 4
    then_image_contains_test_data(image)


def test_DiskImage_for_sddrive_should_contain_4_sides_with_blank_data_when_no_data_is_provided():
    image = DiskImage(typeOfDiskImage=TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE)
    assert len(image.sides) == 4
    then_image_contains_blank_data(image)
