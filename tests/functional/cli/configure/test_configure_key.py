from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive_local_tools.cli.cli_tester import CLITester


async def assert_key_exists(wallet: AsyncUnlockedWallet, private_key: PrivateKey, *, should_exists: bool) -> None:
    exists = await wallet.has_matching_private_key(key=private_key.calculate_public_key().value)

    if should_exists:
        assert exists, "Beekeeper should have given private key."
    else:
        assert not exists, "Beekeeper should not have given private key."


async def test_configure_key_add(cli_tester: CLITester) -> None:
    """Check clive configure key add command."""
    # ARRANGE
    pk = PrivateKey.create()
    unlocked_wallet = cli_tester.world.wallets.user_wallet
    await assert_key_exists(unlocked_wallet, pk, should_exists=False)

    # ACT
    cli_tester.configure_key_add(key=pk.value, alias="add_key")

    # ASSERT
    await assert_key_exists(unlocked_wallet, pk, should_exists=True)


async def test_negative_configure_key_add_in_locked(
    cli_tester_locked: CLITester,
) -> None:
    """Check if clive configure add_key command throws exception when wallet is locked."""
    # ARRANGE
    pk = PrivateKey.create()
    message = CLINoProfileUnlockedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.configure_key_add(key=pk.value, alias="add_key")


@pytest.mark.parametrize("from_beekeeper", [True, False])
async def test_configure_key_remove(cli_tester: CLITester, *, from_beekeeper: bool) -> None:
    """Check clive configure key remove command."""
    # ARRANGE
    pk = PrivateKey.create()
    unlocked_wallet = cli_tester.world.wallets.user_wallet
    await assert_key_exists(unlocked_wallet, pk, should_exists=False)
    cli_tester.configure_key_add(key=pk.value, alias="key")
    await assert_key_exists(unlocked_wallet, pk, should_exists=True)

    # ACT
    cli_tester.configure_key_remove(alias="key", from_beekeeper=from_beekeeper)

    # ASSERT
    await assert_key_exists(unlocked_wallet, pk, should_exists=not from_beekeeper)


async def test_negative_configure_key_remove_in_locked(
    cli_tester_locked: CLITester,
) -> None:
    """Check if clive configure key remove command throws exception when wallet is locked."""
    # ARRANGE
    message = CLINoProfileUnlockedError.MESSAGE

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_locked.configure_key_remove(alias="doesnt-matter")
