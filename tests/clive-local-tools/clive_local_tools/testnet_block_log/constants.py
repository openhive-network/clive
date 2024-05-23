from __future__ import annotations

from string import ascii_lowercase
from typing import Final

import test_tools as tt

WITNESSES: Final[list[tt.Account]] = [tt.Account(name) for name in [f"witness-{i:02d}" for i in range(1, 41)]]
WITNESSES_COUNT: Final[int] = len(WITNESSES)
PROPOSALS = [f"proposal-{c}" for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]

ALT_WORKING_ACCOUNT1: Final[tt.Account] = tt.Account("mary")
ALT_WORKING_ACCOUNT2: Final[tt.Account] = tt.Account("jane")

ALT_WORKING_ACCOUNT1_WITNESS_VOTES_START: Final[int] = 1
ALT_WORKING_ACCOUNT1_WITNESS_VOTES_COUNT: Final[int] = 2
ALT_WORKING_ACCOUNT2_WITNESS_VOTES_START: Final[int] = 0
ALT_WORKING_ACCOUNT2_WITNESS_VOTES_COUNT: Final[int] = 30

WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT: Final[int] = 1
