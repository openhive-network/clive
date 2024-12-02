from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.models.schemas import CustomJsonOperation, TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.command_options import option_to_string
from clive_local_tools.cli.helpers import run_clive_in_subprocess
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.helpers import get_transaction_id_from_output
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


async def test_default_profile(
    prepare_profile: Profile,  # noqa: ARG001
    alt_prepare_profile: Profile,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ACT
    output = run_clive_in_subprocess(["clive", "show", "profile"])

    # ASSERT
    assert f"Profile name: {WORKING_ACCOUNT_NAME}" in output


async def test_custom_profile(prepare_profile: Profile, alt_prepare_profile: Profile, node: tt.RawNode) -> None:  # noqa: ARG001
    # ACT
    output = run_clive_in_subprocess(["clive", "show", "profile", f"--profile-name={ALT_WORKING_ACCOUNT1_NAME}"])

    # ASSERT
    assert f"Profile name: {ALT_WORKING_ACCOUNT1_NAME}" in output


async def test_custom_profile_in_custom_json_operation(
    prepare_beekeeper_wallet: None,  # noqa: ARG001
    alt_prepare_beekeeper_wallet: None,  # noqa: ARG001
    node: tt.RawNode,
) -> None:
    # ARRANGE
    custom_json: Final[str] = '{"foo": "bar"}'
    custom_id: Final[str] = "some_id"
    operation = CustomJsonOperation(
        required_auths=[],
        required_posting_auths=[ALT_WORKING_ACCOUNT1_NAME],
        id_=custom_id,
        json_=custom_json,
    )
    command = [
        "clive",
        "process",
        "custom-json",
        f"--profile-name={ALT_WORKING_ACCOUNT1_NAME}",
        f"--id={custom_id}",
        f"--json={custom_json}",
        f"--sign={ALT_WORKING_ACCOUNT1_KEY_ALIAS}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)
    transaction_id = get_transaction_id_from_output(output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)


async def test_negative_no_default_profile(node: tt.RawNode) -> None:  # noqa: ARG001
    # ARRANGE
    expected_error = "Missing option '--profile-name'."

    # ACT
    with pytest.raises(AssertionError) as exception_info:
        run_clive_in_subprocess(["clive", "show", "balances"])

    # ASSERT
    assert expected_error in str(exception_info.value)


async def test_default_profile_without_working_account(
    prepare_profile_without_working_account: Profile,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ACT
    # ASSERT
    run_clive_in_subprocess(["clive", "show", "chain"])


async def test_negative_default_profile_without_working_account(
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


async def test_custom_profile_and_custom_working_account(
    prepare_profile: Profile,  # noqa: ARG001
    alt_prepare_profile: Profile,  # noqa: ARG001
    node: tt.RawNode,  # noqa: ARG001
) -> None:
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[0]
    command = [
        "clive",
        "show",
        "balances",
        f"--profile-name={ALT_WORKING_ACCOUNT1_NAME}",
        f"--account-name={other_account_name}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)

    # ASSERT
    assert f"Balances of `{other_account_name}` account" in output


async def test_custom_profile_and_custom_authority_in_custom_json_operation(
    prepare_beekeeper_wallet: None,  # noqa: ARG001
    alt_prepare_beekeeper_wallet: None,  # noqa: ARG001
    node: tt.RawNode,
) -> None:
    # ARRANGE
    custom_json: Final[str] = '{"foo": "bar"}'
    custom_id: Final[str] = "some_id"
    operation = CustomJsonOperation(
        required_auths=[],
        required_posting_auths=[WORKING_ACCOUNT_NAME],
        id_=custom_id,
        json_=custom_json,
    )
    command = [
        "clive",
        "process",
        "custom-json",
        f"--profile-name={ALT_WORKING_ACCOUNT1_NAME}",
        f"--id={custom_id}",
        f"--json={custom_json}",
        f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
        f"--authorize={WORKING_ACCOUNT_NAME}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)
    transaction_id = get_transaction_id_from_output(output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)


async def test_default_working_account_in_transfer(
    prepare_beekeeper_wallet: None,  # noqa: ARG001
    node: tt.RawNode,
) -> None:
    # ARRANGE
    other_account_name = WATCHED_ACCOUNTS_NAMES[1]
    amount = tt.Asset.Hive(13.17)
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
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
        f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
    ]

    # ACT
    output = run_clive_in_subprocess(command)
    transaction_id = get_transaction_id_from_output(output)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, operation)
