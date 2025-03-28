from __future__ import annotations

from enum import Enum

FIRST_REVISION = "c600278a"


class Version(Enum):
    V0 = FIRST_REVISION
    V1 = "v1"
    V2 = "v2"

    @property
    def num(self) -> int:
        if self == Version.V0:
            return 0
        return int(self.value[1:])

    def __lt__(self, other: Version) -> bool:
        return self.num < other.num

    def __le__(self, other: Version) -> bool:
        return self.num <= other.num
