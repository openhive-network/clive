from __future__ import annotations

from typing import Final, get_args

from clive.__private.core.types import AlreadySignedMode

ALREADY_SIGNED_MODES: Final[tuple[AlreadySignedMode, ...]] = get_args(AlreadySignedMode)
ALREADY_SIGNED_MODE_DEFAULT: Final[AlreadySignedMode] = "strict"
