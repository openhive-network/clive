from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DEPOSIT: Final[tt.Asset.TestT] = tt.Asset.Test(1)


@pytest.mark.parametrize("amount", [tt.Asset.Hive(1), tt.Asset.Hbd(1)])
@pytest.mark.parametrize("frequency", ["24h", "1d", "1w"])
@pytest.mark.parametrize("pair_id", [0, 1, 2])
@pytest.mark.parametrize("repeat", [2, 3, 4])
async def test_transfer_schedule_create(
    cli_tester: CLITester, amount: tt.Asset.HiveT | tt.Asset.HbdT, frequency: str, pair_id: int, repeat: int
) -> None:
    checkers.assert_no_exit_code_error(
        cli_tester.process_transfer_schedule_create(
            amount=amount,
            from_=WORKING_ACCOUNT_DATA.account.name,
            to="bob",
            frequency=frequency,
            pair_id=pair_id,
            repeat=repeat,
            memo="test_transfer_schedule_create",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    )


@pytest.mark.parametrize("amount", [tt.Asset.Hive(1), tt.Asset.Hbd(1)])
@pytest.mark.parametrize("frequency", ["24h", "1d", "1w"])
@pytest.mark.parametrize("repeat", [2, 3, 4])
@pytest.mark.parametrize("memo", ["mem1", "mem2"])
async def test_transfer_schedule_modify(
    cli_tester: CLITester,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
    frequency: str,
    repeat: int,
    memo: str,
) -> None:
    checkers.assert_no_exit_code_error(
        cli_tester.process_transfer_schedule_create(
            amount=AMOUNT_TO_DEPOSIT,
            from_=WORKING_ACCOUNT_DATA.account.name,
            to="bob",
            frequency="24h",
            repeat=2,
            memo="test_transfer_schedule_modify",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    )

    checkers.assert_no_exit_code_error(
        cli_tester.process_transfer_schedule_modify(
            from_=WORKING_ACCOUNT_DATA.account.name,
            to="bob",
            amount=amount,
            frequency=frequency,
            repeat=repeat,
            memo=memo,
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    )


@pytest.mark.parametrize("pair_id", [0, 1, 2])
async def test_transfer_schedule_remove(
    cli_tester: CLITester,
    pair_id: int,
) -> None:
    checkers.assert_no_exit_code_error(
        cli_tester.process_transfer_schedule_create(
            amount=AMOUNT_TO_DEPOSIT,
            from_=WORKING_ACCOUNT_DATA.account.name,
            to="bob",
            frequency="24h",
            repeat=2,
            pair_id=pair_id,
            memo="test_transfer_schedule_remove",
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    )
    checkers.assert_no_exit_code_error(
        cli_tester.process_transfer_schedule_remove(
            from_=WORKING_ACCOUNT_DATA.account.name,
            to="bob",
            pair_id=pair_id,
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
        )
    )
