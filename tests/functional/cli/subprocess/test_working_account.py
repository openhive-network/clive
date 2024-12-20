from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.models.schemas import CustomJsonOperation, TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.command_options import option_to_string
from clive_local_tools.cli.helpers import run_clive_in_subprocess
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT2_KEY_ALIAS,
)
from clive_local_tools.helpers import get_transaction_id_from_output
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_NAME,
    ALT_WORKING_ACCOUNT2_DATA,
    ALT_WORKING_ACCOUNT2_NAME,
    WATCHED_ACCOUNTS_NAMES,
)

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester


async def import_key(unlocked_world_cm: World, private_key: PrivateKeyAliased) -> None:
    unlocked_world_cm.profile.keys.add_to_import(private_key)
    await unlocked_world_cm.commands.sync_data_with_beekeeper()
    unlocked_world_cm.profile.save()  # save imported key aliases


async def test_unlocked_profile(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,  # noqa: ARG001
) -> None:
    # ACT
    output = run_clive_in_subprocess(["clive", "show", "profile"])

    # ASSERT
    assert f"Profile name: {ALT_WORKING_ACCOUNT1_NAME}" in output


async def test_negative_no_unlocked_profile(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester_with_session_token_locked: CLITester,  # noqa: ARG001
) -> None:
    # ARRANGE
    expected_error = CLINoProfileUnlockedError.MESSAGE

    # ACT
    with pytest.raises(AssertionError) as exception_info:
        run_clive_in_subprocess(["clive", "show", "balances"])

    # ASSERT
    assert expected_error in str(exception_info.value)


async def test_unlocked_profile_without_working_account(
    prepare_profile_without_working_account: Profile,  # noqa: ARG001
    cli_tester: CLITester,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ACT
    # ASSERT
    run_clive_in_subprocess(["clive", "show", "chain"])


async def test_negative_unlocked_profile_without_working_account(
    prepare_profile_without_working_account: Profile,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ARRANGE
    expected_error = "Working account is not set"

    # ACT
    with pytest.raises(AssertionError) as exception_info:
        run_clive_in_subprocess(["clive", "show", "balances"])

    # ASSERT
    assert expected_error in str(exception_info.value)


async def test_unlocked_profile_and_custom_working_account(
    prepare_profile: Profile,  # noqa: ARG001
    cli_tester: CLITester,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[0]
    command = [
        "clive",
        "show",
        "balances",
        f"--account-name={other_account_name}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)

    # ASSERT
    assert f"Balances of `{other_account_name}` account" in output


async def test_custom_authority_in_custom_json_operation(
    prepare_beekeeper_wallet: World,
    node: tt.RawNode,
    cli_tester: CLITester,  # noqa: ARG001
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
    command = [
        "clive",
        "process",
        "custom-json",
        f"--id={custom_id}",
        f"--json={custom_json}",
        f"--sign={ALT_WORKING_ACCOUNT2_KEY_ALIAS}",
        f"--authorize={ALT_WORKING_ACCOUNT2_NAME}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)
    transaction_id = get_transaction_id_from_output(output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)


async def test_default_working_account_in_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,  # noqa: ARG001
) -> None:
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[1]
    amount = tt.Asset.Hive(13.17)
    operation = TransferOperation(
        from_=ALT_WORKING_ACCOUNT1_NAME,
        to=other_account_name,
        amount=amount,
        memo="",
    )
    command = [
        "clive",
        "process",
        "transfer",
        f"--to={other_account_name}",
        f"--amount={option_to_string(amount)}",
        f"--sign={ALT_WORKING_ACCOUNT1_KEY_ALIAS}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)
    transaction_id = get_transaction_id_from_output(output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)
