from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.models.schemas import CustomJsonOperation, TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT2_KEY_ALIAS,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.helpers import get_transaction_id_from_output
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT2_DATA,
    ALT_WORKING_ACCOUNT2_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester


async def import_key(unlocked_world_cm: World, private_key: PrivateKeyAliased) -> None:
    unlocked_world_cm.profile.keys.add_to_import(private_key)
    await unlocked_world_cm.commands.sync_data_with_beekeeper()
    await unlocked_world_cm.commands.save_profile()  # save imported key aliases


async def test_perform_working_account_load_does_not_influence_unrelated_commands(cli_tester: CLITester) -> None:
    """Command `clive show chain` needs profile but doesn't need working account set."""
    # ARRANGE
    cli_tester.world.profile.accounts.unset_working_account()
    await cli_tester.world.commands.save_profile()

    # ACT
    # ASSERT
    cli_tester.show_chain()


async def test_negative_unlocked_profile_without_working_account(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "Working account is not set"
    cli_tester.world.profile.accounts.unset_working_account()
    await cli_tester.world.commands.save_profile()

    # ACT
    with pytest.raises(AssertionError) as exception_info:
        cli_tester.show_balances()

    # ASSERT
    assert expected_error in str(exception_info.value)


async def test_explicitly_given_account_name_overrides_perform_working_account_load(cli_tester: CLITester) -> None:
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[0]

    # ACT
    result = cli_tester.show_balances(account_name=other_account_name)

    # ASSERT
    assert f"Balances of `{other_account_name}` account" in result.output


async def test_custom_authority_in_custom_json_operation(
    prepare_beekeeper_wallet: World,
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    other_key = PrivateKeyAliased(
        value=ALT_WORKING_ACCOUNT2_DATA.account.private_key, alias=ALT_WORKING_ACCOUNT2_KEY_ALIAS
    )
    await import_key(prepare_beekeeper_wallet, other_key)
    custom_json: Final[str] = '{"foo": "bar"}'
    custom_id: Final[str] = "some_id"
    operation = CustomJsonOperation(
        required_auths=[],
        required_posting_auths=[ALT_WORKING_ACCOUNT2_NAME],
        id_=custom_id,
        json_=custom_json,
    )

    # ACT
    result = cli_tester.process_custom_json(
        id_=custom_id, json_=custom_json, sign=ALT_WORKING_ACCOUNT2_KEY_ALIAS, authorize=ALT_WORKING_ACCOUNT2_NAME
    )
    transaction_id = get_transaction_id_from_output(result.output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)


async def test_perform_working_account_load_in_regular_operations(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Command `clive process transfer` needs argument `working_account` or profile needs working account set."""
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[1]
    amount = tt.Asset.Hive(13.17)
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=other_account_name,
        amount=amount,
        memo="",
    )

    # ACT
    result = cli_tester.process_transfer(to=other_account_name, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)
    transaction_id = get_transaction_id_from_output(result.output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)
