from __future__ import annotations

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
from clive.core.url import Url
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from textual.pilot import Pilot


def create_working_account(wallet: tt.Wallet) -> None:
    wallet.create_account(
        WORKING_ACCOUNT.name,
        hives=tt.Asset.Test(1000).as_nai(),
        vests=tt.Asset.Test(1000).as_nai(),
        hbds=tt.Asset.Tbd(1000).as_nai(),
    )
    # Supplying savings:
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Test(100).as_nai(),
        "Supplying HIVE savings",
    )
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Tbd(100).as_nai(),
        "Supplying HBD savings",
    )
    account = wallet.api.get_account(WORKING_ACCOUNT.name)
    tt.logger.debug(f"account: {account}")


def create_watched_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating watched accounts...")
    amount = 1_000
    for account in WATCHED_ACCOUNTS:
        wallet.create_account(
            account.name,
            hives=tt.Asset.Test(amount).as_nai(),
            vests=tt.Asset.Test(amount).as_nai(),
            hbds=tt.Asset.Tbd(amount).as_nai(),
        )
        amount += 1_000


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
        PrivateKeyAliased(value=WORKING_ACCOUNT.private_key._value, alias=f"{WORKING_ACCOUNT.name}_key")
    )
    await world.commands.sync_data_with_beekeeper()
    await Deactivate(
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        wallet=world.profile_data.name,
    ).execute()


@pytest.fixture()
async def world() -> AsyncIterator[TextualWorld]:
    prepare_profile()

    async with TextualWorld() as world:
        yield world


@pytest.fixture()
async def prepared_env(world: TextualWorld) -> tuple[tt.InitNode, Clive]:
    node = tt.InitNode()
    node.config.plugin.append("account_history_rocksdb")
    node.config.plugin.append("account_history_api")
    node.config.plugin.append("reputation_api")
    node.config.plugin.append("rc_api")
    node.config.plugin.append("transaction_status_api")
    node.run()

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    create_working_account(wallet)
    create_watched_accounts(wallet)

    app = Clive.app_instance()

    Clive.world = world
    await prepare_wallet(world)
    await world.node.set_address(Url.parse(node.http_endpoint, protocol="http"))

    return node, app


@pytest.fixture()
async def prepared_tui_on_dashboard(
    prepared_env: tuple[tt.InitNode, Clive]
) -> AsyncIterator[tuple[tt.InitNode, Pilot[int]]]:
    node, app = prepared_env
    async with app.run_test() as pilot:
        yield node, pilot
        await clive_quit(pilot)
