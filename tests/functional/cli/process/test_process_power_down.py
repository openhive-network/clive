from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli.checkers import assert_exit_code, assert_no_pending_power_down, assert_pending_power_down
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_DOWN1: Final[tt.Asset.HiveT] = tt.Asset.Test(123.235)
SINGLE_POWER_DOWN1: Final[tt.Asset.HiveT] = AMOUNT_TO_POWER_DOWN1 / 13
AMOUNT_TO_POWER_DOWN2: Final[tt.Asset.VestT] = tt.Asset.Vest(345.456)
SINGLE_POWER_DOWN2: Final[tt.Asset.VestT] = AMOUNT_TO_POWER_DOWN2 / 13
AMOUNT_TO_POWER_DOWN3: Final[tt.Asset.HiveT] = tt.Asset.Test(234.567)
SINGLE_POWER_DOWN3: Final[tt.Asset.HiveT] = AMOUNT_TO_POWER_DOWN3 / 13


@pytest.mark.parametrize(
    ("amount_to_power_down", "single_power_down"),
    [
        (AMOUNT_TO_POWER_DOWN1, SINGLE_POWER_DOWN1),
        (AMOUNT_TO_POWER_DOWN2, SINGLE_POWER_DOWN2),
    ],
)
async def test_power_down_start_success(
    cli_tester: CLITester,
    amount_to_power_down: tt.Asset.HiveT | tt.Asset.VestT,
    single_power_down: tt.Asset.HiveT | tt.Asset.VestT,
) -> None:
    # ACT
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=amount_to_power_down
    )

    # ASSERT
    assert_pending_power_down(cli_tester, single_power_down)


async def test_power_down_start_fail(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN1
    )
    expected_error = "Power-down is already in progress"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_start_exception_info:
        cli_tester.process_power_down_start(
            password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN3
        )

    # ASSERT
    assert_exit_code(power_down_start_exception_info, 1)


@pytest.mark.parametrize(
    ("amount_to_power_down", "single_power_down"),
    [
        (AMOUNT_TO_POWER_DOWN1, SINGLE_POWER_DOWN1),
        (AMOUNT_TO_POWER_DOWN2, SINGLE_POWER_DOWN2),
    ],
)
async def test_power_down_restart_create(
    cli_tester: CLITester,
    amount_to_power_down: tt.Asset.HiveT | tt.Asset.VestT,
    single_power_down: tt.Asset.HiveT | tt.Asset.VestT,
) -> None:
    # ACT
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=amount_to_power_down
    )

    # ASSERT
    assert_pending_power_down(cli_tester, single_power_down)


async def test_power_down_restart_override(cli_tester: CLITester) -> None:
    # ARRNGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN1
    )

    # ACT
    cli_tester.process_power_down_restart(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN3
    )

    # ASSERT
    assert_pending_power_down(cli_tester, SINGLE_POWER_DOWN3)


async def test_power_down_cancel_success(cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_power_down_start(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, amount=AMOUNT_TO_POWER_DOWN1
    )

    # ACT
    cli_tester.process_power_down_cancel(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_no_pending_power_down(cli_tester)


async def test_power_down_cancel_fail(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "network_broadcast_api.broadcast_transaction"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as power_down_cancel_exception_info:
        cli_tester.process_power_down_cancel(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_exit_code(power_down_cancel_exception_info, 1)
