from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_exit_code
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from schemas.fields.basic import PublicKey


AMOUNT_TO_POWER_DOWN: Final[tt.Asset.HiveT] = tt.Asset.Test(123.235)
AMOUNT_TO_POWER_DOWN2: Final[tt.Asset.HiveT] = tt.Asset.Test(234.567)


async def test_power_down_start_success(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ASSERT


async def test_power_down_start_fail(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )
    expected_error = "Power-down is already in progress"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_start_exception_info:
        cli_tester.process_power_down_start(
            password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN2
        )

    # ASSERT
    assert_exit_code(power_down_start_exception_info, 1)


async def test_power_down_restart_create(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ASSERT


async def test_power_down_restart_override(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ACT
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN2
    )

    # ASSERT


async def test_power_down_cancel_success(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN
    )

    # ACT
    cli_tester.process_power_down_cancel(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT


async def test_power_down_cancel_fail(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "network_broadcast_api.broadcast_transaction"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_cancel_exception_info:
        cli_tester.process_power_down_cancel(
            password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
        )

    # ASSERT
    assert_exit_code(power_down_cancel_exception_info, 1)
