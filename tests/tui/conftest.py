from __future__ import annotations

from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import TextualWorld
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.app import Clive
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.core.url import Url
from clive_local_tools.testnet_block_log import (
    get_alternate_chain_spec_path,
    get_block_log,
    get_config,
    get_time_offset,
)
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.activate import activate
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import wait_for_screen
from clive_local_tools.tui.utils import get_mode

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


def prepare_profile() -> None:
    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()


async def prepare_wallet(world: TextualWorld) -> None:
    password = await CreateWallet(
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        wallet=WORKING_ACCOUNT.name,
        password=WORKING_ACCOUNT.name,
    ).execute_with_result()

    tt.logger.info(f"password for {WORKING_ACCOUNT.name} is: `{password}`")
    world.profile_data.working_account.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT.private_key, alias=f"{WORKING_ACCOUNT.name}_key")
    )
    await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
async def world() -> AsyncIterator[TextualWorld]:
    prepare_profile()

    async with TextualWorld() as world:
        yield world


@pytest.fixture()
async def prepared_env(world: TextualWorld) -> tuple[tt.RawNode, tt.Wallet, Clive]:
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

    app = Clive.app_instance()

    Clive.world = world
    await prepare_wallet(world)
    await world.node.set_address(Url.parse(node.http_endpoint.as_string()))

    return node, wallet, app


@pytest.fixture()
async def prepared_tui_on_dashboard_inactive(
    world: TextualWorld,
    prepared_env: tuple[tt.RawNode, tt.Wallet, Clive],
) -> AsyncIterator[tuple[tt.RawNode, tt.Wallet, ClivePilot]]:
    node, wallet, app = prepared_env
    await Deactivate(
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        wallet=world.profile_data.name,
    ).execute()
    async with app.run_test() as pilot:
        yield node, wallet, pilot
        await clive_quit(pilot)


@pytest.fixture()
async def prepared_tui_on_dashboard_active(
    world: TextualWorld,
    prepared_env: tuple[tt.RawNode, tt.Wallet, Clive],
) -> AsyncIterator[tuple[tt.RawNode, tt.Wallet, ClivePilot]]:
    node, wallet, app = prepared_env
    # Temporary code - waits until the problem with the application status is resolved (DashboardInactive vs DashboardActive)
    await Deactivate(
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        wallet=world.profile_data.name,
    ).execute()
    async with app.run_test() as pilot:
        await activate(pilot, app.world.profile_data.name)
        # End of temporary code
        assert get_mode(pilot.app) == "active", "Expected 'active' mode!"
        await wait_for_screen(pilot, DashboardActive)
        yield node, wallet, pilot
        await clive_quit(pilot)
