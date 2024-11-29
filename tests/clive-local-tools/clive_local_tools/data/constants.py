from __future__ import annotations

from typing import Final

from clive.__private.core.constants.setting_identifiers import (
    BEEKEEPER_REMOTE_ADDRESS,
    BEEKEEPER_SESSION_TOKEN,
    NODE_CHAIN_ID,
    SECRETS_NODE_ADDRESS,
)
from clive.__private.settings import clive_prefixed_envvar
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA, WORKING_ACCOUNT_DATA

TESTNET_CHAIN_ID: Final[str] = "18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"

WORKING_ACCOUNT_PASSWORD: Final[str] = WORKING_ACCOUNT_DATA.account.name
WORKING_ACCOUNT_KEY_ALIAS: Final[str] = f"{WORKING_ACCOUNT_DATA.account.name}_key"
ALT_WORKING_ACCOUNT1_PASSWORD: Final[str] = ALT_WORKING_ACCOUNT1_DATA.account.name
ALT_WORKING_ACCOUNT1_KEY_ALIAS: Final[str] = f"{ALT_WORKING_ACCOUNT1_DATA.account.name}_key"
BEEKEEPER_REMOTE_ADDRESS_ENV_NAME: Final[str] = clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)
BEEKEEPER_SESSION_TOKEN_ENV_NAME: Final[str] = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
NODE_CHAIN_ID_ENV_NAME: Final[str] = clive_prefixed_envvar(NODE_CHAIN_ID)
NODE_ADDRESS_ENV_NAME: Final[str] = clive_prefixed_envvar(SECRETS_NODE_ADDRESS)
