from __future__ import annotations

from string import ascii_lowercase
from typing import Final

import test_tools as tt

WITNESSES = [f"witness-{i:03d}" for i in range(60)]
PROPOSALS = [f"proposal-{c}" for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]

WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT: Final[int] = 1
