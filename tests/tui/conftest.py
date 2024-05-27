from __future__ import annotations

from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.app import Clive
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.operations import Operations
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_screen_active,
)
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    wait_for_screen,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from _pytest.fixtures import SubRequest

    from clive_local_tools.tui.types import ClivePilot

    NodeWithWallet = tuple[tt.RawNode, tt.Wallet]
    PreparedTuiEnv = tuple[tt.RawNode, tt.Wallet, ClivePilot]


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


@pytest.fixture()
def working_account(request: SubRequest) -> tt.Account:
    if hasattr(request.node, "callspec"):
        params = request.node.callspec.params
    else:
        return WORKING_ACCOUNT_DATA.account
    return params.get("account", WORKING_ACCOUNT_DATA.account)  # type: ignore[no-any-return]


@pytest.fixture()
async def prepare_profile(working_account: tt.Account) -> ProfileData:
    profile_data = ProfileData(
        working_account.name,
        working_account=WorkingAccount(name=working_account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    profile_data.save()
    return profile_data


@pytest.fixture()
async def world() -> World:
    return World()  # will load last profile by default


@pytest.fixture()
async def prepare_beekeeper_wallet(working_account: tt.Account, prepare_profile: ProfileData, world: World) -> None:  # noqa: ARG001
    async with world:
        (await world.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)).raise_if_error_occurred()

        world.profile_data.keys.add_to_import(
            PrivateKeyAliased(value=working_account.private_key, alias=WORKING_ACCOUNT_KEY_ALIAS)
        )
        await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
def node_with_wallet(working_account: tt.Account) -> NodeWithWallet:
    node = run_node(use_faketime=True)

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(working_account.private_key)
    account = wallet.api.get_account(working_account.name)
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
        await wait_for_screen(pilot, DashboardInactive)

        yield node, wallet, pilot

        await clive_quit(pilot)


@pytest.fixture()
async def prepared_tui_on_dashboard_inactive(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    return prepared_env


@pytest.fixture()
async def prepared_tui_on_dashboard_active(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    node, wallet, pilot = prepared_env
    await pilot.pause()  # required, otherwise next call to self.app inside Commands will fail with NoActiveAppError
    await pilot.app.world.commands.activate(password=WORKING_ACCOUNT_PASSWORD)
    await wait_for_screen(pilot, DashboardActive)
    return prepared_env


@pytest.fixture()
async def prepared_tui_on_witnesses_screen(prepared_tui_on_dashboard_active: PreparedTuiEnv) -> PreparedTuiEnv:
    _, _, pilot = prepared_tui_on_dashboard_active
    assert_is_screen_active(pilot, DashboardActive)
    await press_and_wait_for_screen(pilot, "f2", Operations)
    assert_active_tab(pilot, "Financial")
    await pilot.press("right")
    assert_active_tab(pilot, "Social")
    await pilot.press("right")
    assert_active_tab(pilot, "Governance")
    await focus_next(pilot)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")
    return prepared_tui_on_dashboard_active
