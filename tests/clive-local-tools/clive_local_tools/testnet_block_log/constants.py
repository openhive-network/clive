from __future__ import annotations

from string import ascii_lowercase
from typing import Final

import test_tools as tt

from clive_local_tools.data.generates import generate_proposal_name, generate_witness_name

WITNESSES: Final[list[tt.Account]] = [tt.Account(name) for name in [generate_witness_name(i) for i in range(60)]]
PROPOSALS: Final[list[str]] = [generate_proposal_name(c) for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]
EMPTY_ACCOUNT: Final[tt.Account] = tt.Account("carol")
ALT_WORKING_ACCOUNT1: Final[tt.Account] = tt.Account("mary")
ALT_WORKING_ACCOUNT2: Final[tt.Account] = tt.Account("jane")

WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT: Final[int] = 1

WORKING_ACCOUNT_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100_000)
WORKING_ACCOUNT_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(100_000)
WORKING_ACCOUNT_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100_000)  # in hive power

WATCHED_ACCOUNT_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(1_000)
WATCHED_ACCOUNT_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(1_000)
WATCHED_ACCOUNT_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(1_000)  # in hive power

WORKING_ACCOUNT_HIVE_SAVINGS_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100)
WORKING_ACCOUNT_HBD_SAVINGS_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(200)
WORKING_ACCOUNT_HBD_SAVINGS_WITHDRAWAL: Final[tt.Asset.TbdT] = tt.Asset.Tbd(10)

ALT_WORKING_ACCOUNT1_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(110_000)
ALT_WORKING_ACCOUNT1_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(111_000)
ALT_WORKING_ACCOUNT1_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(112_000)  # in hive power

ALT_WORKING_ACCOUNT2_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(120_000)
ALT_WORKING_ACCOUNT2_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(121_000)
ALT_WORKING_ACCOUNT2_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(122_000)  # in hive power
