from __future__ import annotations

from string import ascii_lowercase
from typing import Final

import test_tools as tt

from clive_local_tools.data.generates import generate_proposal_name, generate_witness_name
from clive_local_tools.data.models import AccountData

WITNESS_FIRST_INDEX: Final[int] = 1
WITNESS_LAST_INDEX: Final[int] = 40

WITNESSES: Final[list[tt.Account]] = [
    tt.Account(name) for name in [generate_witness_name(i) for i in range(WITNESS_FIRST_INDEX, WITNESS_LAST_INDEX + 1)]
]
PROPOSALS: Final[list[str]] = [generate_proposal_name(c) for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
EMPTY_ACCOUNT: Final[tt.Account] = tt.Account("carol")
WORKING_ACCOUNT_DATA: Final[AccountData] = AccountData(
    account=tt.Account("alice"),
    hives_liquid=tt.Asset.Test(100_000),
    hbds_liquid=tt.Asset.Tbd(100_000),
    vests=tt.Asset.Test(100_000),  # in hive power
    hives_savings=tt.Asset.Test(100),
    hives_savings_withdrawal=tt.Asset.Test(0),
    hbds_savings=tt.Asset.Tbd(200),
    hbds_savings_withdrawal=tt.Asset.Tbd(10),
)
WATCHED_ACCOUNTS_DATA: Final[list[AccountData]] = [
    AccountData(
        account=tt.Account(name),
        hives_liquid=tt.Asset.Test(1_000),
        hbds_liquid=tt.Asset.Tbd(1_000),
        vests=tt.Asset.Test(1_000),  # in hive power
    )
    for name in ("bob", "timmy", "john")
]
ALT_WORKING_ACCOUNT1_DATA: Final[AccountData] = AccountData(
    account=tt.Account("mary"),
    hives_liquid=tt.Asset.Test(110_000),
    hbds_liquid=tt.Asset.Tbd(111_000),
    vests=tt.Asset.Test(112_000),  # in hive power
    voted_witnesses=[WITNESSES[i].name for i in range(1, 3)],
)
ALT_WORKING_ACCOUNT2_DATA: Final[AccountData] = AccountData(
    account=tt.Account("jane"),
    hives_liquid=tt.Asset.Test(120_000),
    hbds_liquid=tt.Asset.Tbd(121_000),
    vests=tt.Asset.Test(122_000),  # in hive power
    voted_witnesses=[WITNESSES[i].name for i in range(30)],
)
