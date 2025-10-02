from __future__ import annotations

from typing import Final, get_args

from clive.__private.core.types import AuthorityLevel, AuthorityLevelRegular

AUTHORITY_LEVELS_REGULAR: Final[tuple[AuthorityLevelRegular, ...]] = tuple(
    authority_level for authority_level in get_args(AuthorityLevelRegular)
)
AUTHORITY_LEVELS: Final[tuple[AuthorityLevel, ...]] = tuple(
    authority_level for union_member in get_args(AuthorityLevel) for authority_level in get_args(union_member)
)
