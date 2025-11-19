"""Shared constants for Script Interface process tests."""

from __future__ import annotations

from typing import Final

import test_tools as tt

from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

# Test accounts
RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
SECOND_RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[1].account.name

# Test amounts
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
AMOUNT2: Final[tt.Asset.HiveT] = tt.Asset.Hive(2)

# Test memos
MEMO: Final[str] = "test-process-transfer-memo"
MEMO2: Final[str] = "test-process-transfer-memo-second"

# Test keys
TEST_KEY: Final[str] = "STM5tE6iiVkizDrhPU6pAGxFuW38gWJS2Vemue1nYtZ3Zn9zh4Dhn"
TEST_KEY2: Final[str] = "STM7sw22HqsXbz7D2CmJfmMwt9rimJTmqGHHVuT8uN9MqKUVESTrU"

# Re-export commonly used constants
__all__ = [
    "ALT_WORKING_ACCOUNT1_KEY_ALIAS",
    "AMOUNT",
    "AMOUNT2",
    "MEMO",
    "MEMO2",
    "RECEIVER",
    "SECOND_RECEIVER",
    "TEST_KEY",
    "TEST_KEY2",
    "WATCHED_ACCOUNTS_DATA",
    "WORKING_ACCOUNT_DATA",
    "WORKING_ACCOUNT_KEY_ALIAS",
    "WORKING_ACCOUNT_NAME",
]
