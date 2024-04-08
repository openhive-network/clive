from __future__ import annotations

from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import TextualWorld
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.app import Clive
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.core.url import Url
from clive_local_tools.testnet_block_log import (
    get_alternate_chain_spec_path,
    get_block_log,
    get_config,
    get_time_offset,
)
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import wait_for_screen

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot

    PreparedTuiEnv = tuple[tt.RawNode, tt.Wallet, ClivePilot]


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


def _prepare_profile() -> None:
    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()


async def _prepare_beekeeper_wallet(world: TextualWorld) -> None:
    password = (await world.commands.create_wallet(password=WORKING_ACCOUNT.name)).result_or_raise
    tt.logger.info(f"password for {WORKING_ACCOUNT.name} is: `{password}`")

    world.profile_data.working_account.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT.private_key, alias=f"{WORKING_ACCOUNT.name}_key")
    )
    await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
def _node_with_wallet() -> tuple[tt.RawNode, tt.Wallet]:  # noqa: PT005 # not intended for direct usage
    config_lines = get_config().write_to_lines()
    block_log = get_block_log()
    alternate_chain_spec_path = get_alternate_chain_spec_path()
    node = tt.RawNode()
    node.config.load_from_lines(config_lines)
    arguments = ["--alternate-chain-spec", str(alternate_chain_spec_path)]
    time_offset = get_time_offset()
    node.run(replay_from=block_log, arguments=arguments, time_control=time_offset)

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(WORKING_ACCOUNT.private_key)
    account = wallet.api.get_account(WORKING_ACCOUNT.name)
    tt.logger.debug(f"working account: {account}")

    return node, wallet


@pytest.fixture()
async def _world(  # noqa: PT005 # not intended for direct usage
    _node_with_wallet: tuple[tt.RawNode, tt.Wallet],
) -> AsyncIterator[TextualWorld]:
    node, _ = _node_with_wallet

    _prepare_profile()

    async with TextualWorld() as world:
        await world.node.set_address(Url.parse(node.http_endpoint.as_string()))
        yield world


@pytest.fixture()
async def prepared_env(
    _world: TextualWorld, _node_with_wallet: tuple[tt.RawNode, tt.Wallet]
) -> AsyncIterator[PreparedTuiEnv]:
    node, wallet = _node_with_wallet
    world = _world

    app = Clive.app_instance()
    Clive.world = world

    pilot: ClivePilot
    async with app.run_test() as pilot:
        await _prepare_beekeeper_wallet(world)

        if world.app_state.is_active and isinstance(app.screen, DashboardInactive):
            # beekeeper create wallet makes app active, we have to ensure correct dashboard to be displayed
            await app.switch_screen("dashboard_active")

        await wait_for_screen(pilot, DashboardActive)

        yield node, wallet, pilot

        await clive_quit(pilot)


@pytest.fixture()
async def prepared_tui_on_dashboard_inactive(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    node, wallet, pilot = prepared_env
    await pilot.pause()  # required, otherwise next call to self.app inside Commands will fail with NoActiveAppError
    await pilot.app.world.commands.deactivate()  # we have to deactivate because by default we are in active state triggered by create_wallet
    return node, wallet, pilot


@pytest.fixture()
async def prepared_tui_on_dashboard_active(prepared_env: PreparedTuiEnv) -> PreparedTuiEnv:
    return prepared_env
