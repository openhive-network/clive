from __future__ import annotations

from typing import Final, get_args

from clive.__private.core.types import AuthorityLevel, AuthorityLevelRegular

AUTHORITY_LEVELS_REGULAR: Final[tuple[AuthorityLevelRegular, ...]] = get_args(AuthorityLevelRegular)

AUTHORITY_LEVELS: Final[tuple[AuthorityLevel, ...]] = get_args(AuthorityLevel)

DEFAULT_AUTHORITY_THRESHOLD: Final[int] = 1
DEFAULT_AUTHORITY_WEIGHT: Final[int] = 1

MODIFIED_PREFIX: Final[str] = "*(modified) "
