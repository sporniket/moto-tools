"""
Controller.
---
(c) 2022~2024 David SPORN
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

from .image import DiskSide
from .catalog import (
    CatalogEntry,
    CatalogEntryRecord,
    CatalogEntryStatus,
    TypeOfDiskFile,
    TypeOfData,
)
from .block_allocation import BlockAllocation, BlockStatus

RESERVED_BLOCKS = [0, 40, 41]


def _computeRequiredSlots(sizeOfData: int, sizeOfSlot: int) -> (int, int):
    requiredSlots = sizeOfData // sizeOfSlot
    usageOfLastSlot = sizeOfData % sizeOfSlot
    if usageOfLastSlot > 0:
        requiredSlots = requiredSlots + 1
    else:
        usageOfLastSlot = sizeOfSlot
    return (requiredSlots, usageOfLastSlot)


def _computeTrackSectorOfBlock(blockId: int, diskSide: DiskSide) -> (int, int):
    return (diskSide.tracks[blockId // 2], (blockId & 1) * 8)


def _batToBytes(bat: list[BlockAllocation]) -> bytes:
    result = bytearray(256)
    result[1 : len(bat)] = [b.status for b in bat]
    return bytes(result)


class FileSystemUsage:
    def __init__(self, used: int, reserved: int, free: int):
        self.used = used
        self.reserved = reserved
        self.free = free


class FileSystemController:
    def __init__(self, diskSide: DiskSide):
        self._diskSide = diskSide

    @property
    def _bat(self) -> list[BlockAllocation]:
        batSector = self._diskSide.tracks[20].sectors[1].dataOfPayload
        return [BlockAllocation(i - 1, batSector[i]) for i in range(1, 161)]

    @_bat.setter
    def _bat(self, bat: list[BlockAllocation]):
        batSector = bytearray(256)
        batSector[1 : len(bat) + 1] = [b.status for b in bat]
        self._diskSide.tracks[20].sectors[1].dataOfPayload = batSector

    def listFiles(
        self,
        *,
        excludeDeletedEntries: bool = True,
        excludeNeverUsedEntries: bool = True,
    ) -> list[CatalogEntry]:
        bat = self._bat
        result = []
        for s in range(2, 16):  # catalog is from sector 2 to 15 of track 20
            catSector = self._diskSide.tracks[20].sectors[s].dataOfPayload
            for start in range(0, 256, 32):  # a catalog entry every 32 bytes
                entry = CatalogEntry.fromBytes(catSector[start : start + 32], bat)
                if (
                    excludeNeverUsedEntries
                    and entry.status == CatalogEntryStatus.NEVER_USED
                ):
                    continue
                if excludeDeletedEntries and entry.status == CatalogEntryStatus.DELETED:
                    continue
                result.append(entry)

        return result

    def readFile(self, file: CatalogEntry) -> bytes:
        usageDict = file.toUsageDict()
        if usageDict is None:
            return bytes([])
        blocks, lastBlockUsage, lastSectorSize = (
            usageDict["blocks"],
            usageDict["usageOfLastBlock"],
            usageDict["usageOfLastSector"],
        )

        # sanity check
        fileDict = file.toDict()
        fileName, fileExtension = fileDict["name"], fileDict["extension"]
        if len(blocks) == 0:
            return bytes()
        if lastBlockUsage == 0:
            raise ValueError(
                f"invalid.last.block.usage:{lastBlockUsage}:{fileName.rstrip()}.{fileExtension.rstrip()}"
            )

        # proceeds
        result = bytearray(file.toDict()["sizeInBytes"])

        index = 0
        lastI = len(blocks) - 1
        for i, b in enumerate(blocks):
            track, firstSector = _computeTrackSectorOfBlock(b, self._diskSide)

            sMax, lastSize = (
                (lastBlockUsage, lastSectorSize) if i == lastI else (8, 255)
            )
            lastS = sMax - 1

            for s in range(sMax):
                sector = track.sectors[firstSector + s].dataOfPayload
                if s == lastS:
                    result[index : index + lastSize] = sector[0:lastSize]
                    index = index + lastSize
                else:
                    result[index : index + 255] = sector[0:255]
                    index = index + 255

        return result

    def writeFile(
        self,
        content: bytes or bytearray,
        name: str,
        extension: str,
        *,
        typeOfFile: TypeOfDiskFile = TypeOfDiskFile.BASIC_DATA,
        typeOfData: TypeOfData = TypeOfData.BINARY_DATA,
    ):
        # checks that there is enough space, otherwise error
        # find the first free block
        # while there is data to write, fill the block, find the next free block
        # --> first block, last block usage, last sector usage
        # update block allocation table
        # find first available entry in catalog
        # create CatalogEntry (name/extension is uppercased)
        # write CatalogEntry in sector

        bat = self._bat
        dataLen = len(content)

        requiredSectorLength, usageOfLastSector = _computeRequiredSlots(dataLen, 255)
        requiredBlockLength, usageOfLastBlock = _computeRequiredSlots(
            requiredSectorLength, 8
        )

        batBlocks = [b for b in bat if b.isFree()][:requiredBlockLength]
        if len(batBlocks) < requiredBlockLength:
            raise ValueError(
                f"not.enough.blocks:require.{requiredBlockLength}:got.{len(batBlocks)}"
            )

        # copy of data into disk image
        currentBlock = 0
        currentSector = 0
        lastBlockIndex = requiredBlockLength - 1
        for currentSliceIndex in range(0, dataLen, 255):
            # for each sector to write
            if currentSector == 0:
                # if sector counter is 0 : find track/first sector of block
                track, firstSector = _computeTrackSectorOfBlock(
                    batBlocks[currentBlock].id, self._diskSide
                )
                # and update the BAT block, by the way
                if currentBlock >= lastBlockIndex:
                    batBlocks[currentBlock].setupAsLastBlock(usageOfLastBlock)
                else:
                    batBlocks[currentBlock].linkTo(batBlocks[currentBlock + 1])
            # write slice to sector
            track.sectors[firstSector + currentSector].dataOfPayload = content[
                currentSliceIndex : currentSliceIndex + 255
            ]
            if currentSector == 7:
                # if last sector of block, bump current block
                currentBlock = currentBlock + 1
            # bump sector counter
            currentSector = (currentSector + 1) % 8

        # update BAT
        self._bat = bat

        firstBlock = batBlocks[0].id
        entryRecord = CatalogEntryRecord(
            name=name.upper(),
            extension=extension.upper(),
            typeOfFile=typeOfFile,
            typeOfData=typeOfData,
            firstBlock=batBlocks[0].id,
            usageOfLastSector=usageOfLastSector,
        )

        # Find a free catalog entry and write the new entry
        found = False
        for s in range(2, 16):  # catalog is from sector 2 to 15 of track 20
            catSector = bytearray(self._diskSide.tracks[20].sectors[s].dataOfPayload)
            for start in range(0, 256, 32):  # a catalog entry every 32 bytes
                entry = CatalogEntry.fromBytes(catSector[start : start + 32], bat)
                if (
                    entry.status == CatalogEntryStatus.NEVER_USED
                    or entry.status == CatalogEntryStatus.DELETED
                ):
                    catSector[start : start + 32] = entryRecord.toBytes()
                    self._diskSide.tracks[20].sectors[s].dataOfPayload = catSector
                    found = True
                    break
            if found:
                break

        if not found:
            # restore BAT
            for b in batBlocks:
                b.setFree()
            self._bat = bat
            raise ValueError("no.more.space.in.catalog")

    def initFileSystem(self):
        # reset bat
        bat = [
            BlockAllocation(
                i,
                (
                    BlockStatus.RESERVED.value
                    if i in RESERVED_BLOCKS
                    else BlockStatus.FREE.value
                ),
            )
            for i in range(160)
        ]
        self._bat = bat

        # fill catalog sectors with 0xff
        empty_sector = bytes([0xFF for i in range(256)])
        for s in range(2, 16):  # catalog is from sector 2 to 15 of track 20
            self._diskSide.tracks[20].sectors[s].dataOfPayload = empty_sector

    def computeUsage(self) -> FileSystemUsage:
        used = 0
        free = 0
        reserved = 0
        for ba in self._bat:
            if ba.isFree():
                free = free + 1
            elif ba.isReserved():
                reserved = reserved + 1
            else:
                used = used + 1
        return FileSystemUsage(used, reserved, free)
