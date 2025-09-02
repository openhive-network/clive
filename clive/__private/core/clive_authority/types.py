from __future__ import annotations

from typing import Literal

AuthorityLevelRegular = Literal["owner", "active", "posting"]
AuthorityLevelMemo = Literal["memo"]
AuthorityLevel = AuthorityLevelRegular | AuthorityLevelMemo
