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
)
from .block_allocation import BlockAllocation


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
        return [BlockAllocation(i, batSector[i]) for i in range(160)]

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
        if len(blocks) == 0:
            raise ValueError(f"invalid.no.blocks.in.use")
        if lastBlockUsage == 0:
            raise ValueError(f"invalid.last.block.usage:{lastBlockUsage}")
        if lastSectorSize == 0:
            raise ValueError(f"invalid.last.sector.usage:{lastSectorSize}")

        # proceeds
        result = bytearray(file.toDict()["sizeInBytes"])

        index = 0
        lastI = len(blocks) - 1
        for i, b in enumerate(blocks):
            track = self._diskSide.tracks[b // 2]
            firstSector = (b & 1) * 8

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
