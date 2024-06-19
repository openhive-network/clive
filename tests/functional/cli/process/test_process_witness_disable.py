from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.models import Asset
from clive_local_tools.cli.checkers import assert_exit_code
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


SIGNING_KEY = WORKING_ACCOUNT_DATA.account.public_key
FEE: Final[Asset.Hive] = Asset.hive(5)
ACCOUNT_CREATION_FEE: Final[Asset.Hive] = Asset.hive(50)


async def test_disable_success(node: tt.RawNode, cli_tester: CLITester) -> None:
    # PREPARE
    cli_tester.process_witness_create(
        url="http://url.html",
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    cli_tester.process_witness_disable(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_disable_fail(node: tt.RawNode, cli_tester: CLITester) -> None:
    # PREPARE
    expected_error = "is not witness"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as witness_disable_exception_info:
        cli_tester.process_witness_disable(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_exit_code(witness_disable_exception_info, 1)


async def test_double_disable(node: tt.RawNode, cli_tester: CLITester) -> None:
    # PREPARE
    cli_tester.process_witness_create(
        url="http://url.html",
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    cli_tester.process_witness_disable(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)
    expected_error = "is already disabled"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as witness_disable_exception_info:
        cli_tester.process_witness_disable(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_exit_code(witness_disable_exception_info, 1)
