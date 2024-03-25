from __future__ import annotations

from string import ascii_lowercase
from typing import Final

import test_tools as tt

TESTNET_CHAIN_ID: Final[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"

WITNESSES = [f"witness-{i:03d}" for i in range(60)]
PROPOSALS = [f"proposal-{c}" for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]
EMPTY_ACCOUNT: Final[tt.Account] = tt.Account("carol")

WORKING_ACCOUNT_PASSWORD: Final[str] = WORKING_ACCOUNT.name

WORKING_ACCOUNT_KEY_ALIAS: Final[str] = f"{WORKING_ACCOUNT.name}_key"

WORKING_ACCOUNT_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100_000)
WORKING_ACCOUNT_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(100_000)
WORKING_ACCOUNT_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100_000)

WATCHED_ACCOUNT_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(1_000)
WATCHED_ACCOUNT_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(1_000)
WATCHED_ACCOUNT_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(1_000)

WORKING_ACCOUNT_HIVE_SAVINGS_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(100)
WORKING_ACCOUNT_HBD_SAVINGS_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(200)
WORKING_ACCOUNT_HBD_SAVINGS_WITHDRAWAL: Final[tt.Asset.TbdT] = tt.Asset.Tbd(10)
