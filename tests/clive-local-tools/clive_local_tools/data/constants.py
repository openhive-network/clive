from __future__ import annotations

from typing import Final

from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA, EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

TESTNET_CHAIN_ID: Final[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"

WORKING_ACCOUNT_PASSWORD: Final[str] = WORKING_ACCOUNT_DATA.account.name
WORKING_ACCOUNT_KEY_ALIAS: Final[str] = f"{WORKING_ACCOUNT_DATA.account.name}_key"
ALT_WORKING_ACCOUNT1_PASSWORD: Final[str] = ALT_WORKING_ACCOUNT1_DATA.account.name
ALT_WORKING_ACCOUNT1_KEY_ALIAS: Final[str] = f"{ALT_WORKING_ACCOUNT1_DATA.account.name}_key"
EMPTY_ACCOUNT_PASSWORD: Final[str] = f"{EMPTY_ACCOUNT.name}_key"
EMPTY_ACCOUNT_KEY_ALIAS: Final[str] = f"{EMPTY_ACCOUNT.name}_key"
