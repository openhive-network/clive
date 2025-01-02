from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.models.schemas import TransferToVestingOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA, EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Hive(654.321)
OTHER_ACCOUNT: Final[tt.Account] = ALT_WORKING_ACCOUNT1_DATA.account


async def import_key(unlocked_world_cm: World, private_key: PrivateKeyAliased) -> None:
    unlocked_world_cm.profile.keys.add_to_import(private_key)
    await unlocked_world_cm.commands.sync_data_with_beekeeper()
    unlocked_world_cm.profile.save()  # save imported key aliases


async def test_power_up_to_other_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    operation = TransferToVestingOperation(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(amount=AMOUNT_TO_POWER_UP, to=operation.to, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_power_up_no_default_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    other_account_key_alias: Final[str] = f"{OTHER_ACCOUNT.name}_key"
    other_key = PrivateKeyAliased(value=OTHER_ACCOUNT.private_key, alias=other_account_key_alias)
    async with World() as world_cm:
        await import_key(world_cm, other_key)

    operation = TransferToVestingOperation(
        from_=OTHER_ACCOUNT.name,
        to=EMPTY_ACCOUNT.name,
        amount=AMOUNT_TO_POWER_UP,
    )

    # ACT
    result = cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP, from_=operation.from_, to=operation.to, sign=other_account_key_alias
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
    result = cli_tester.process_power_up(amount=AMOUNT_TO_POWER_UP, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
