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
from moto_lib import TypeOfDiskImage, TypeOfDiskFile


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
