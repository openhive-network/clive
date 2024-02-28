from __future__ import annotations

from typing import Final

import test_tools as tt

TESTNET_CHAIN_ID: Final[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]

WORKING_ACCOUNT_PASSWORD: Final[str] = WORKING_ACCOUNT.name

WORKING_ACCOUNT_KEY_ALIAS: Final[str] = f"{WORKING_ACCOUNT.name}_key"

WORKING_ACCOUNT_HIVE_LIQUID_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(1234)
WORKING_ACCOUNT_HBD_LIQUID_BALANCE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(2345)
WORKING_ACCOUNT_VEST_BALANCE: Final[tt.Asset.TestT] = tt.Asset.Test(3456)
