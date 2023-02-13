from __future__ import annotations

from typing import Final

from dunamai import Version

VERSION: Final[Version] = Version.from_git()

VERSION_INFO: Final[str] = f"{VERSION.base} ({VERSION.commit}) {'dirty!' if VERSION.dirty else ''}"
