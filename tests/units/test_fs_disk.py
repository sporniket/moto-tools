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
from moto_lib import TypeOfDiskImage, TypeOfDiskFile, DiskTrack


######################################################## Test suite for TypeOfDiskImage


def test_TypeOfDiskImage_should_verify_expectations():
    then_TypeOfDiskImage_verify_expectations(
        TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE, 0, 256
    )
    then_TypeOfDiskImage_verify_expectations(
        TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE, 1, 512
    )


def then_TypeOfDiskImage_verify_expectations(
    typeOfImage: TypeOfDiskImage, intValue: int, sizeOfSector: int
):
    assert TypeOfDiskImage.fromInt(intValue) == typeOfImage
    assert typeOfImage.sizeOfSector() == sizeOfSector


######################################################## Test suite for TypeOfDiskFile


def test_TypeOfDiskFile_should_verify_expectations():
    then_TypeOfDiskFile_verify_expectations(TypeOfDiskFile.BASIC_PROGRAM, 0, "B")
    then_TypeOfDiskFile_verify_expectations(TypeOfDiskFile.BASIC_DATA, 1, "D")
    then_TypeOfDiskFile_verify_expectations(
        TypeOfDiskFile.MACHINE_LANGUAGE_PROGRAM, 2, "M"
    )
    then_TypeOfDiskFile_verify_expectations(TypeOfDiskFile.TEXT_FILE, 3, "A")


def then_TypeOfDiskFile_verify_expectations(
    typeOfFile: TypeOfDiskFile, intValue: int, charValue: str
):
    assert TypeOfDiskFile.fromInt(intValue) == typeOfFile
    assert TypeOfDiskFile.fromCharacterCode(charValue) == typeOfFile
    assert typeOfFile.asCharacterCode() == charValue
    assert typeOfFile.asByte() == intValue


######################################################## Test suite for TypeOfDiskFile


def test_DiskTrack_from_track_data_should_create_correct_sectors():
    def createDummySector(
        value: int,
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        if value < 0 or value > 0xFF:
            raise ValueError("byte is between 0 and 255, got {value}.")
        result = [value for i in range(256)]
        if typeOfDiskImage == TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE:
            result += [0xFF for i in range(256)]
        return result

    def createDummyTrack(
        typeOfDiskImage: TypeOfDiskImage = TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
    ):
        sectorsData = [createDummySector(i, typeOfDiskImage) for i in range(16)]
        result = [b for data in sectorsData for b in data]
        return result

    for t in [
        TypeOfDiskImage.EMULATOR_FLOPPY_IMAGE,
        TypeOfDiskImage.SDDRIVE_FLOPPY_IMAGE,
    ]:
        track = DiskTrack(createDummyTrack(t), typeOfDiskImage=t)
        for i, s in enumerate(track.sectors):
            sdata = s.data
            assert sdata[0] == i
            assert sdata[255] == i
