from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME
from clive_local_tools.tui.utils import unlock_wallet

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper, AsyncUnlockedWallet

    from clive_local_tools.cli.cli_tester import CLITester


async def assert_key_exists(wallet: AsyncUnlockedWallet, private_key: PrivateKey, *, should_exists: bool) -> None:
    exists = await wallet.has_matching_private_key(key=private_key.calculate_public_key().value)

    if should_exists:
        assert exists, "Beekeeper should have given private key."
    else:
        assert not exists, "Beekeeper should not have given private key."


async def test_configure_key_add(beekeeper: AsyncBeekeeper, cli_tester: CLITester) -> None:
    """Check clive configure key add command."""
    # ARRANGE
    pk = PrivateKey.create()
    unlocked_wallet = await unlock_wallet(beekeeper, WORKING_ACCOUNT_NAME, WORKING_ACCOUNT_PASSWORD)
    await assert_key_exists(unlocked_wallet, pk, should_exists=False)

    # ACT
    cli_tester.configure_key_add(key=pk.value, alias="add_key", password=WORKING_ACCOUNT_PASSWORD)

    # ASSERT
    await assert_key_exists(unlocked_wallet, pk, should_exists=True)


@pytest.mark.parametrize("from_beekeeper", [True, False])
async def test_configure_key_remove(beekeeper: AsyncBeekeeper, cli_tester: CLITester, *, from_beekeeper: bool) -> None:
    """Check clive configure key remove command."""
    # ARRANGE
    pk = PrivateKey.create()
    unlocked_wallet = await unlock_wallet(beekeeper, WORKING_ACCOUNT_NAME, WORKING_ACCOUNT_PASSWORD)
    await assert_key_exists(unlocked_wallet, pk, should_exists=False)
    cli_tester.configure_key_add(key=pk.value, alias="key", password=WORKING_ACCOUNT_PASSWORD)
    await assert_key_exists(unlocked_wallet, pk, should_exists=True)

    # ACT
    cli_tester.configure_key_remove(alias="key", password=WORKING_ACCOUNT_PASSWORD, from_beekeeper=from_beekeeper)

    # ASSERT
    await assert_key_exists(unlocked_wallet, pk, should_exists=not from_beekeeper)
