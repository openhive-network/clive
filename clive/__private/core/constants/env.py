from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent.parent.parent.parent
LAUNCH_TIME: Final[datetime] = datetime.now()  # noqa: DTZ005; we want to use the local timezone
ENVVAR_PREFIX: Final[str] = "CLIVE"

KNOWN_FIRST_PARTY_PACKAGES: Final[list[str]] = [
    "beekeepy",
    "clive_local_tools",
    "schemas",
    "test_tools",
    "wax",
]

WALLETS_AMOUNT_PER_PROFILE: Final[int] = 2
"""Each profile can have up to 2 wallets: user wallet and encryption wallet."""
