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
from clive.__private.ui.dashboard.dashboard_locked import DashboardLocked
from clive.__private.ui.dashboard.dashboard_unlocked import DashboardUnlocked
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node
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


@pytest.fixture()
async def prepare_profile() -> Profile:
    profile = Profile(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    profile.save()
    return profile


@pytest.fixture()
async def world() -> World:
    return World()  # will load last profile by default


@pytest.fixture()
async def prepare_beekeeper_wallet(prepare_profile: Profile, world: World) -> None:  # noqa: ARG001
    async with world as world_cm:
        (await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)).raise_if_error_occurred()

        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=WORKING_ACCOUNT_KEY_ALIAS)
        )
        await world_cm.commands.sync_data_with_beekeeper()


@pytest.fixture()
def node_with_wallet() -> NodeWithWallet:
    node = run_node(use_faketime=True)

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(WORKING_ACCOUNT_DATA.account.private_key)
    account = wallet.api.get_account(WORKING_ACCOUNT_DATA.account.name)
    tt.logger.debug(f"working account: {account}")

    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())

    return node, wallet


@pytest.fixture()
async def prepared_env(
    node_with_wallet: NodeWithWallet,
    prepare_beekeeper_wallet: None,  # noqa: ARG001
) -> AsyncIterator[PreparedTuiEnv]:
    node, wallet = node_with_wallet

    app = Clive.app_instance()

    pilot: ClivePilot
    async with app.run_test() as pilot:
        await wait_for_screen(pilot, DashboardLocked)

        yield node, wallet, pilot

        await clive_quit(pilot)


@pytest.fixture()
async def prepared_tui_on_dashboard_locked(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    return prepared_env


@pytest.fixture()
async def prepared_tui_on_dashboard_unlocked(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    node, wallet, pilot = prepared_env
    await pilot.pause()  # required, otherwise next call to self.app inside Commands will fail with NoActiveAppError
    await pilot.app.world.commands.unlock(password=WORKING_ACCOUNT_PASSWORD)
    await wait_for_screen(pilot, DashboardUnlocked)
    return prepared_env
