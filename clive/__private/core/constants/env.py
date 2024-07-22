from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

ROOT_DIRECTORY: Final[Path] = Path(__file__).parent.parent.parent.parent
LAUNCH_TIME: Final[datetime] = datetime.now()  # noqa: DTZ005; we want to use the local timezone
