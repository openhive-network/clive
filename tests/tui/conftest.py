from __future__ import annotations

from collections.abc import Callable
from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.logger import logger
from clive.__private.settings import settings
from clive.__private.ui.app import Clive
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.unlock import Unlock
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
    run_node,
)
from clive_local_tools.tui.checkers import assert_is_dashboard, assert_is_screen_active
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import wait_for_screen

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot

    NodeWithWallet = tuple[tt.RawNode, tt.Wallet]
    PreparedTuiEnv = tuple[tt.RawNode, tt.Wallet, ClivePilot]


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


@pytest.fixture
def logger_configuration_factory() -> Callable[[], None]:
    def _logger_configuration_factory() -> None:
        logger.setup(enable_textual=False)

    return _logger_configuration_factory


@pytest.fixture
async def _prepare_profile_with_wallet_tui() -> None:
    """Prepare profile and wallets using locally spawned beekeeper."""
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
        await world_cm.commands.sync_data_with_beekeeper()


@pytest.fixture
def node_with_wallet() -> NodeWithWallet:
    node = run_node(use_faketime=True)

    wallet = tt.Wallet(attach_to=node)
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(WORKING_ACCOUNT_DATA.account.private_key)
    account = wallet.api.get_account(WORKING_ACCOUNT_DATA.account.name)
    tt.logger.debug(f"working account: {account}")

    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())

    return node, wallet


@pytest.fixture
async def prepared_env(
    node_with_wallet: NodeWithWallet,
    _prepare_profile_with_wallet_tui: None,
) -> AsyncIterator[PreparedTuiEnv]:
    node, wallet = node_with_wallet
    async with Clive().run_test() as pilot:
        await wait_for_screen(pilot, Unlock)
        assert_is_screen_active(pilot, Unlock)

        yield node, wallet, pilot

        await clive_quit(pilot)


@pytest.fixture
async def prepared_tui_on_dashboard(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    node, wallet, pilot = prepared_env
    await pilot.app.world.load_profile(WORKING_ACCOUNT_DATA.account.name, WORKING_ACCOUNT_PASSWORD)

    # update the data and resume timers (pilot skips onboarding/unlocking via TUI - updating is handled there)
    await pilot.app.update_alarms_data_on_newest_node_data().wait()
    pilot.app.resume_periodic_intervals()

    await pilot.app.push_screen(Dashboard())
    await wait_for_screen(pilot, Dashboard)
    assert_is_dashboard(pilot)
    return prepared_env
