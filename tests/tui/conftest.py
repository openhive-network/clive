from __future__ import annotations

from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.ui.app import Clive
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.unlock import Unlock
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node
from clive_local_tools.tui.checkers import assert_is_dashboard, assert_is_screen_active
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import wait_for_screen
from clive_local_tools.tui.workaround_incompatibility_with_fixtures import event_loop  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot

    NodeWithWallet = tuple[tt.RawNode, tt.Wallet]
    PreparedTuiEnv = tuple[tt.RawNode, tt.Wallet, ClivePilot]


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


@pytest.fixture
async def prepare_profile() -> Profile:
    return Profile.create(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )


@pytest.fixture
async def world() -> World:
    return World()


@pytest.fixture
async def prepare_beekeeper_wallet(prepare_profile: Profile, world: World) -> None:
    async with world as world_cm:
        await world_cm.switch_profile(prepare_profile)
        await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=WORKING_ACCOUNT_KEY_ALIAS)
        )
        await world_cm.commands.sync_data_with_beekeeper()
        await world_cm.profile.save(world_cm.encryption_service)


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
    prepare_beekeeper_wallet: None,  # noqa: ARG001
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

    await pilot.app.world.commands.unlock(
        profile_name=WORKING_ACCOUNT_DATA.account.name, password=WORKING_ACCOUNT_PASSWORD, permanent=True
    )
    await pilot.app.world.load_profile_based_on_beekepeer()

    # update the data (pilot skips onboarding/unlocking via TUI - updating is handled there)
    await pilot.app.update_alarms_data_asap_on_newest_node_data().wait()

    await pilot.app.push_screen(Dashboard())
    await wait_for_screen(pilot, Dashboard)
    assert_is_dashboard(pilot)
    return prepared_env
