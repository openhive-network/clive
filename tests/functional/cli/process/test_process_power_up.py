from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive_local_tools.checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA, EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA
from schemas.operations import TransferToVestingOperation

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Test(654.321)
OTHER_ACCOUNT: Final[tt.Account] = ALT_WORKING_ACCOUNT1_DATA.account
OTHER_ACCOUNT_KEY_ALIAS: Final[str] = f"{OTHER_ACCOUNT.name}_key"


async def test_power_up_to_other_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        to=operation.to,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_up_no_default_account(world: World, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    async with world as world_cm:
        await world_cm.commands.activate(password=WORKING_ACCOUNT_PASSWORD)
        world_cm.profile_data.keys.add_to_import(
            PrivateKeyAliased(value=OTHER_ACCOUNT.private_key, alias=OTHER_ACCOUNT_KEY_ALIAS),
        )
        await world_cm.commands.sync_data_with_beekeeper()
    operation = TransferToVestingOperation(
        from_=OTHER_ACCOUNT.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        from_=operation.from_,
        to=operation.to,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=OTHER_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_up_default_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=WORKING_ACCOUNT_DATA.account.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=operation.amount,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
