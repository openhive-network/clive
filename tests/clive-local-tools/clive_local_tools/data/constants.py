from __future__ import annotations

from typing import Final

from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT

TESTNET_CHAIN_ID: Final[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"

WORKING_ACCOUNT_PASSWORD: Final[str] = WORKING_ACCOUNT.name
WORKING_ACCOUNT_KEY_ALIAS: Final[str] = f"{WORKING_ACCOUNT.name}_key"
