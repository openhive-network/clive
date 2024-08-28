from __future__ import annotations

from typing import Literal, TypeAlias

from clive.__private.core.authority import AccountAuthority

AuthorityType = Literal["owner", "active", "posting"]
AuthoritiesT: TypeAlias = set[AccountAuthority]
