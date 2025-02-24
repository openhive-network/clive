from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.node import CANCEL_PROXY_VALUE

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester

from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME
from schemas.operations import AccountWitnessProxyOperation

ACCOUNT_NAME: Final[str] = WORKING_ACCOUNT_NAME
PROXY_ACCOUNT_NAME: Final[str] = WATCHED_ACCOUNTS_NAMES[0]


async def test_setting_proxy_to_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    proxy_set_operation = AccountWitnessProxyOperation(account=ACCOUNT_NAME, proxy=PROXY_ACCOUNT_NAME)

    # ACT
    result = cli_tester.process_proxy_set(
        proxy=PROXY_ACCOUNT_NAME, account_name=ACCOUNT_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, proxy_set_operation)


async def test_canceling_proxy_to_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    proxy_clear_operation = AccountWitnessProxyOperation(account=ACCOUNT_NAME, proxy=CANCEL_PROXY_VALUE)
    cli_tester.process_proxy_set(proxy=PROXY_ACCOUNT_NAME, account_name=ACCOUNT_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    result = cli_tester.process_proxy_clear(account_name=ACCOUNT_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, proxy_clear_operation)


async def test_canceling_not_existing_proxy(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_message = "Assert Exception:account.has_proxy()"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_message):
        cli_tester.process_proxy_clear(account_name=ACCOUNT_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS)
