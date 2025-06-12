from __future__ import annotations

from pathlib import Path
from string import ascii_lowercase
from typing import Final

import test_tools as tt

from clive.__private.core.known_exchanges import KnownExchanges
from clive_local_tools.data.generates import generate_proposal_name, generate_witness_name
from clive_local_tools.data.models import AccountData

BLOCK_LOG_WITH_CONFIG_DIRECTORY: Final[Path] = Path(__file__).parent / "block_log_with_config"

WITNESSES: Final[list[tt.Account]] = [tt.Account(name) for name in [generate_witness_name(i) for i in range(60)]]
PROPOSALS: Final[list[str]] = [generate_proposal_name(c) for c in ascii_lowercase]

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
EMPTY_ACCOUNT: Final[tt.Account] = tt.Account("carol")
WORKING_ACCOUNT_NAME: Final[str] = "alice"
WORKING_ACCOUNT_DATA: Final[AccountData] = AccountData(
    account=tt.Account(WORKING_ACCOUNT_NAME),
    hives_liquid=tt.Asset.Test(100_000),
    hbds_liquid=tt.Asset.Tbd(100_000),
    vests=tt.Asset.Test(100_000),  # in hive power
    hives_savings=tt.Asset.Test(100),
    hives_savings_withdrawal=tt.Asset.Test(0),
    hbds_savings=tt.Asset.Tbd(200),
    hbds_savings_withdrawal=tt.Asset.Tbd(10),
)
WATCHED_ACCOUNTS_NAMES: Final[list[str]] = ["bob", "timmy", "john"]
WATCHED_ACCOUNTS_DATA: Final[list[AccountData]] = [
    AccountData(
        account=tt.Account(name),
        hives_liquid=tt.Asset.Test(1_000),
        hbds_liquid=tt.Asset.Tbd(1_000),
        vests=tt.Asset.Test(1_000),  # in hive power
    )
    for name in WATCHED_ACCOUNTS_NAMES
]
ALT_WORKING_ACCOUNT1_NAME: Final[str] = "mary"
ALT_WORKING_ACCOUNT1_DATA: Final[AccountData] = AccountData(
    account=tt.Account(ALT_WORKING_ACCOUNT1_NAME),
    hives_liquid=tt.Asset.Test(110_000),
    hbds_liquid=tt.Asset.Tbd(111_000),
    vests=tt.Asset.Test(112_000),  # in hive power
)
ALT_WORKING_ACCOUNT2_NAME: Final[str] = "jane"
ALT_WORKING_ACCOUNT2_DATA: Final[AccountData] = AccountData(
    account=tt.Account(ALT_WORKING_ACCOUNT2_NAME),
    hives_liquid=tt.Asset.Test(120_000),
    hbds_liquid=tt.Asset.Tbd(121_000),
    vests=tt.Asset.Test(122_000),  # in hive power
)

UNKNOWN_ACCOUNT: Final[str] = "null"

KNOWN_EXCHANGES_NAMES: Final[list[str]] = [exchange.name for exchange in KnownExchanges()]

KNOWN_ACCOUNTS: Final[list[str]] = [
    EMPTY_ACCOUNT.name,
    *WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_NAME,
    ALT_WORKING_ACCOUNT1_NAME,
    ALT_WORKING_ACCOUNT2_NAME,
    *KNOWN_EXCHANGES_NAMES,
]
