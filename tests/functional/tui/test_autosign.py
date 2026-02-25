from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS, SELECT_FILE_ROOT_PATH
from clive.__private.core.keys.keys import PrivateKey, PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.models.schemas import TransferOperation
from clive.__private.settings import get_settings
from clive.__private.ui.app import Clive
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.dialogs import SaveTransactionToFileDialog
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.operations import Operations, TransferToAccount
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.screens.unlock import Unlock
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_transaction_file_is_signed
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_DATA,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
    run_node,
)
from clive_local_tools.tui.checkers import assert_is_dashboard, assert_is_screen_active
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.notifications import (
    extract_message_from_notification,
    extract_transaction_id_from_notification,
)
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import focus_next, press_and_wait_for_screen, wait_for_screen, write_text

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

    from clive_local_tools.tui.types import ClivePilot


RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
EXTRA_KEY_1_ALIAS: Final[str] = "extra_key_1"
EXTRA_KEY_2_ALIAS: Final[str] = "extra_key_2"


@pytest.fixture
async def prepared_tui_autosign(request: pytest.FixtureRequest) -> AsyncIterator[tuple[tt.RawNode, ClivePilot]]:
    """Set up TUI with 3 keys in wallet, 2 in active authority, threshold from request.param."""
    threshold: int = request.param

    extra_key_1 = PrivateKey.generate()
    extra_key_2 = PrivateKey.generate()

    node = run_node()
    wallet = tt.Wallet(attach_to=node)
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(WORKING_ACCOUNT_DATA.account.private_key)

    # Add extra_key_1 to alice's active authority and set threshold
    wallet.api.update_account_auth_key(WORKING_ACCOUNT_NAME, "active", extra_key_1.calculate_public_key().value, 1)
    wallet.api.update_account_auth_threshold(WORKING_ACCOUNT_NAME, "active", threshold)
    node.wait_number_of_blocks(1)

    get_settings().set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())

    # Profile with 3 keys: alice's key, extra_key_1 (in authority), extra_key_2 (unrelated)
    async with World() as world_cm:
        await world_cm.create_new_profile_with_wallets(
            name=WORKING_ACCOUNT_NAME,
            password=WORKING_ACCOUNT_PASSWORD,
            working_account=WORKING_ACCOUNT_NAME,
            watched_accounts=WATCHED_ACCOUNTS_NAMES,
        )
        await world_cm.commands.sync_state_with_beekeeper()
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=WORKING_ACCOUNT_KEY_ALIAS)
        )
        world_cm.profile.keys.add_to_import(PrivateKeyAliased(value=extra_key_1.value, alias=EXTRA_KEY_1_ALIAS))
        world_cm.profile.keys.add_to_import(PrivateKeyAliased(value=extra_key_2.value, alias=EXTRA_KEY_2_ALIAS))
        await world_cm.commands.sync_data_with_beekeeper()

    async with Clive().run_test() as pilot:
        await wait_for_screen(pilot, Unlock)
        await pilot.app.world.load_profile(WORKING_ACCOUNT_NAME, WORKING_ACCOUNT_PASSWORD)
        await pilot.app.update_alarms_data_on_newest_node_data().wait()
        pilot.app.resume_periodic_intervals()
        await pilot.app.push_screen(Dashboard())
        await wait_for_screen(pilot, Dashboard)
        assert_is_dashboard(pilot)

        yield node, pilot

        await clive_quit(pilot)


@pytest.mark.parametrize("prepared_tui_autosign", [1, 2], indirect=True)
async def test_autosign_tui_with_three_wallet_keys_two_in_authority(
    prepared_tui_autosign: tuple[tt.RawNode, ClivePilot],
) -> None:
    """Test autosign in TUI with 3 wallet keys (2 in authority) successfully broadcasts a transfer."""
    node, pilot = prepared_tui_autosign

    expected_operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo="",
    )

    # ACT - navigate to transfer and fill in data
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    await write_text(pilot, RECEIVER)  # AccountNameInput (initial focus)
    await focus_next(pilot)  # → LiquidAssetAmountInput
    await write_text(pilot, str(AMOUNT.as_float()))
    await focus_next(pilot)  # → token select
    await choose_asset_token(pilot, "HIVE")
    await focus_next(pilot)  # → MemoInput
    await focus_next(pilot)  # → exit MemoInput (Autosign is pre-selected in TransactionSummary)

    await process_operation(pilot, "FINALIZE_TRANSACTION")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.fixture
async def prepared_tui_autosign_insufficient() -> AsyncIterator[ClivePilot]:
    """Set up TUI with 2 keys in wallet, neither of which is in alice's active authority."""
    extra_key_1 = PrivateKey.generate()
    extra_key_2 = PrivateKey.generate()

    node = run_node()

    get_settings().set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())

    async with World() as world_cm:
        await world_cm.create_new_profile_with_wallets(
            name=WORKING_ACCOUNT_NAME,
            password=WORKING_ACCOUNT_PASSWORD,
            working_account=WORKING_ACCOUNT_NAME,
            watched_accounts=WATCHED_ACCOUNTS_NAMES,
        )
        await world_cm.commands.sync_state_with_beekeeper()
        world_cm.profile.keys.add_to_import(PrivateKeyAliased(value=extra_key_1.value, alias=EXTRA_KEY_1_ALIAS))
        world_cm.profile.keys.add_to_import(PrivateKeyAliased(value=extra_key_2.value, alias=EXTRA_KEY_2_ALIAS))
        await world_cm.commands.sync_data_with_beekeeper()

    async with Clive().run_test() as pilot:
        await wait_for_screen(pilot, Unlock)
        await pilot.app.world.load_profile(WORKING_ACCOUNT_NAME, WORKING_ACCOUNT_PASSWORD)
        await pilot.app.update_alarms_data_on_newest_node_data().wait()
        pilot.app.resume_periodic_intervals()
        await pilot.app.push_screen(Dashboard())
        await wait_for_screen(pilot, Dashboard)
        assert_is_dashboard(pilot)

        yield pilot

        await clive_quit(pilot)


async def test_negative_autosign_tui_with_insufficient_authority(
    prepared_tui_autosign_insufficient: ClivePilot,
) -> None:
    """Test that autosign fails and stays on TransactionSummary when wallet keys don't match alice's authority."""
    from clive.__private.core.commands.autosign import InsufficientKeysAutoSignError  # noqa: PLC0415

    pilot = prepared_tui_autosign_insufficient

    # ACT - navigate to transfer and attempt to broadcast via autosign
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    await write_text(pilot, RECEIVER)  # AccountNameInput (initial focus)
    await focus_next(pilot)  # → LiquidAssetAmountInput
    await write_text(pilot, str(AMOUNT.as_float()))
    await focus_next(pilot)  # → token select
    await choose_asset_token(pilot, "HIVE")
    await focus_next(pilot)  # → MemoInput
    await focus_next(pilot)  # → exit MemoInput

    await press_and_wait_for_screen(
        pilot, CLIVE_PREDEFINED_BINDINGS.operations.finalize_transaction.key, TransactionSummary
    )
    await pilot.press(CLIVE_PREDEFINED_BINDINGS.transaction_summary.broadcast.key)

    # ASSERT - error notification shown, still on TransactionSummary
    error_reason = InsufficientKeysAutoSignError.REASON

    def find_autosign_error(message: str) -> str:
        return error_reason if error_reason in message else ""

    found = await extract_message_from_notification(pilot, find_autosign_error)
    assert found == error_reason
    assert_is_screen_active(pilot, TransactionSummary)


async def _navigate_to_transaction_summary_via_transfer(pilot: ClivePilot) -> None:
    """Fill in a transfer form and navigate to TransactionSummary."""
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    await write_text(pilot, RECEIVER)
    await focus_next(pilot)
    await write_text(pilot, str(AMOUNT.as_float()))
    await focus_next(pilot)
    await choose_asset_token(pilot, "HIVE")
    await focus_next(pilot)
    await focus_next(pilot)

    await press_and_wait_for_screen(
        pilot, CLIVE_PREDEFINED_BINDINGS.operations.finalize_transaction.key, TransactionSummary
    )


@pytest.mark.parametrize("prepared_tui_autosign", [1, 2], indirect=True)
async def test_autosign_tui_save_transaction_to_file(
    prepared_tui_autosign: tuple[tt.RawNode, ClivePilot],
    tmp_path: Path,
) -> None:
    """Test that autosign correctly signs and saves a transaction to file via TUI."""
    _node, pilot = prepared_tui_autosign

    save_path = tmp_path / "transaction.json"
    get_settings().set(SELECT_FILE_ROOT_PATH, str(tmp_path))

    # ACT
    await _navigate_to_transaction_summary_via_transfer(pilot)
    await press_and_wait_for_screen(
        pilot, CLIVE_PREDEFINED_BINDINGS.transaction_summary.save_transaction_to_file.key, SaveTransactionToFileDialog
    )
    await write_text(pilot, save_path.name)
    await press_and_wait_for_screen(pilot, "enter", TransactionSummary)

    # ASSERT
    assert save_path.exists(), "Transaction file should have been saved"
    assert_transaction_file_is_signed(save_path)


async def test_negative_autosign_tui_save_transaction_to_file_with_insufficient_authority(
    prepared_tui_autosign_insufficient: ClivePilot,
    tmp_path: Path,
) -> None:
    """Test that autosign fails and keeps the save dialog open when wallet keys don't match alice's authority."""
    from clive.__private.core.commands.autosign import InsufficientKeysAutoSignError  # noqa: PLC0415

    pilot = prepared_tui_autosign_insufficient

    save_path = tmp_path / "transaction.json"
    get_settings().set(SELECT_FILE_ROOT_PATH, str(tmp_path))

    # ACT
    await _navigate_to_transaction_summary_via_transfer(pilot)
    await press_and_wait_for_screen(
        pilot, CLIVE_PREDEFINED_BINDINGS.transaction_summary.save_transaction_to_file.key, SaveTransactionToFileDialog
    )
    await write_text(pilot, save_path.name)
    await pilot.press("enter")

    # ASSERT - error notification shown, dialog stays open, file was not saved
    error_reason = InsufficientKeysAutoSignError.REASON

    def find_autosign_error(message: str) -> str:
        return error_reason if error_reason in message else ""

    found = await extract_message_from_notification(pilot, find_autosign_error)
    assert found == error_reason
    assert_is_screen_active(pilot, SaveTransactionToFileDialog)
    assert not save_path.exists(), "Transaction file should not have been saved on autosign failure"

    await press_and_wait_for_screen(pilot, "escape", TransactionSummary)
