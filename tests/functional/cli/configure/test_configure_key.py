from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive_local_tools.cli.cli_tester import CLITester


async def assert_key_exists(beekeeper: Beekeeper, private_key: PrivateKey, *, should_exists: bool) -> None:
    exists = (
        await beekeeper.api.has_matching_private_key(
            wallet_name=WORKING_ACCOUNT_NAME, public_key=private_key.calculate_public_key().value
        )
    ).exists

    if should_exists:
        assert exists, "Beekeeper should have given private key."
    else:
        assert not exists, "Beekeeper should not have given private key."


async def test_configure_key_add(beekeeper: Beekeeper, cli_tester: CLITester) -> None:
    """Check clive configure key add command."""
    # ARRANGE
    pk = PrivateKey.create()
    await assert_key_exists(beekeeper, pk, should_exists=False)

    # ACT
    cli_tester.configure_key_add(key=pk.value, alias="add_key")

    # ASSERT
    await assert_key_exists(beekeeper, pk, should_exists=True)


async def test_configure_key_add_with_beekeeper_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
) -> None:
    """Check if clive configure add_key command throws exception when wallet is not unlocked using session token."""
    # ARRANGE
    pk = PrivateKey.create()
    message = CLINoProfileUnlockedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.configure_key_add(key=pk.value, alias="add_key")


@pytest.mark.parametrize("from_beekeeper", [True, False])
async def test_configure_key_remove(beekeeper: Beekeeper, cli_tester: CLITester, *, from_beekeeper: bool) -> None:
    """Check clive configure key remove command."""
    # ARRANGE
    pk = PrivateKey.create()
    await assert_key_exists(beekeeper, pk, should_exists=False)
    cli_tester.configure_key_add(key=pk.value, alias="key")
    await assert_key_exists(beekeeper, pk, should_exists=True)

    # ACT
    cli_tester.configure_key_remove(alias="key", from_beekeeper=from_beekeeper)

    # ASSERT
    await assert_key_exists(beekeeper, pk, should_exists=not from_beekeeper)


async def test_configure_key_remove_with_beekeeper_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
) -> None:
    """Check if clive configure key remove command throws exception when wallet is not unlocked using session token."""
    # ARRANGE
    message = CLINoProfileUnlockedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.configure_key_remove(alias="doesnt-matter")
