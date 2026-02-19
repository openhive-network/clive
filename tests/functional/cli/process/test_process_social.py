from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.models.schemas import CustomJsonOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operation_type_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import (
    get_formatted_error_message,
    get_operation_from_transaction,
    get_transaction_id_from_output,
)
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.cli.result_wrapper import CLITestResult

FOLLOWER: Final[str] = WORKING_ACCOUNT_NAME
FOLLOWING: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
BAD_ACCOUNT: Final[str] = AccountManager.get_bad_accounts()[0]


def _assert_social_operation_payload(
    node: tt.RawNode,
    result: CLITestResult,
    *,
    expected_follower: str,
    expected_following: str,
    expected_what: list[str],
) -> None:
    """Verify the payload of a social (follow) CustomJsonOperation in the blockchain."""
    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, CustomJsonOperation)

    assert op.id_ == "follow", f"Expected operation id 'follow', got '{op.id_}'"
    assert expected_follower in op.required_posting_auths, (
        f"Expected {expected_follower} in required_posting_auths, got {op.required_posting_auths}"
    )

    json_value = op.json_.value
    assert isinstance(json_value, list), f"Expected json_ value to be a list, got {type(json_value)}"
    payload = json_value[1]
    assert payload["follower"] == expected_follower, (
        f"Expected follower '{expected_follower}', got '{payload['follower']}'"
    )
    assert payload["following"] == expected_following, (
        f"Expected following '{expected_following}', got '{payload['following']}'"
    )
    assert payload["what"] == expected_what, f"Expected what={expected_what}, got {payload['what']}"


async def test_social_follow(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test clive process social follow command."""
    # ACT
    result = cli_tester.process_social_follow(
        user=FOLLOWING,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    _assert_social_operation_payload(
        node, result, expected_follower=FOLLOWER, expected_following=FOLLOWING, expected_what=["blog"]
    )


async def test_social_unfollow(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test clive process social unfollow command."""
    # ACT
    result = cli_tester.process_social_unfollow(
        user=FOLLOWING,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    _assert_social_operation_payload(
        node, result, expected_follower=FOLLOWER, expected_following=FOLLOWING, expected_what=[""]
    )


async def test_social_mute(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test clive process social mute command."""
    # ACT
    result = cli_tester.process_social_mute(
        user=FOLLOWING,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    _assert_social_operation_payload(
        node, result, expected_follower=FOLLOWER, expected_following=FOLLOWING, expected_what=["ignore"]
    )


async def test_social_unmute(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test clive process social unmute command."""
    # ACT
    result = cli_tester.process_social_unmute(
        user=FOLLOWING,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    _assert_social_operation_payload(
        node, result, expected_follower=FOLLOWER, expected_following=FOLLOWING, expected_what=[""]
    )


async def test_social_follow_dry_run(cli_tester: CLITester) -> None:
    """Test clive process social follow command with --no-broadcast (dry run)."""
    # ACT
    result = cli_tester.process_social_follow(
        user=FOLLOWING,
        broadcast=False,
    )

    # ASSERT
    assert result.exit_code == 0
    assert "dry run" in result.output.lower()


async def test_negative_social_follow_bad_account(cli_tester: CLITester) -> None:
    """Test that following a bad account raises an error."""
    # ARRANGE
    expected_error = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_social_follow(
            user=BAD_ACCOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_social_mute_bad_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test that muting a bad account is allowed."""
    # ACT
    result = cli_tester.process_social_mute(
        user=BAD_ACCOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    assert_operation_type_in_blockchain(node, result, CustomJsonOperation)


async def test_social_follow_with_explicit_account_name(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test clive process social follow command with explicit --account-name."""
    # ACT
    result = cli_tester.process_social_follow(
        account_name=FOLLOWER,
        user=FOLLOWING,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0
    assert_operation_type_in_blockchain(node, result, CustomJsonOperation)


async def test_negative_social_unfollow_bad_account(cli_tester: CLITester) -> None:
    """Test that unfollowing a bad account raises an error."""
    # ARRANGE
    expected_error = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_social_unfollow(
            user=BAD_ACCOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_negative_social_unmute_bad_account(cli_tester: CLITester) -> None:
    """Test that unmuting a bad account raises an error."""
    # ARRANGE
    expected_error = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_social_unmute(
            user=BAD_ACCOUNT,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )
