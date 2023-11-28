from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403
from typer.testing import CliRunner

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive_local_tools.constants import TESTNET_CHAIN_ID

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive.__private.cli.clive_typer import CliveTyper


CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]


@pytest.fixture()
async def cli_with_runner() -> AsyncIterator[tuple[CliveTyper, CliRunner]]:
    """Will run init node, configure profile and return CliRunner from typer.testing module."""
    init_node = tt.InitNode()
    init_node.config.plugin.append("transaction_status_api")
    init_node.config.plugin.append("account_history_api")
    init_node.config.plugin.append("account_history_rocksdb")
    init_node.config.plugin.append("reputation_api")
    init_node.run()

    cli_wallet = tt.Wallet(attach_to=init_node, additional_arguments=["--transaction-serialization", "hf26"])
    cli_wallet.api.import_key(init_node.config.private_key[0])

    with cli_wallet.in_single_transaction():
        creator_account_name = CREATOR_ACCOUNT.name
        for account in [WORKING_ACCOUNT, *WATCHED_ACCOUNTS]:
            key = tt.PublicKey(account.name)
            cli_wallet.api.create_account_with_keys(
                creator_account_name,
                account.name,
                "{}",
                key,
                key,
                key,
                key,
            )
            cli_wallet.api.transfer(creator_account_name, account.name, tt.Asset.Test(1234).as_nai(), "memo")
            cli_wallet.api.transfer_to_vesting(creator_account_name, account.name, tt.Asset.Test(2345).as_nai())
            cli_wallet.api.transfer(creator_account_name, account.name, tt.Asset.Tbd(3445).as_nai(), "memo")

    settings.set("secrets.node_address", f"http://{init_node.http_endpoint}")
    settings.set("node.chain_id", TESTNET_CHAIN_ID)

    working_directory = tt.context.get_current_directory()
    settings.data_path = working_directory
    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()

    async with World(WORKING_ACCOUNT.name) as world:
        await CreateWallet(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet=WORKING_ACCOUNT.name,
            password=WORKING_ACCOUNT.name,
        ).execute_with_result()
        world.profile_data.set_default_profile("alice")
        world.profile_data.save()

        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key._value, alias=f"{WORKING_ACCOUNT.name}_key")
        )
        await world.commands.sync_data_with_beekeeper()
        world.profile_data.set_default_profile("alice")
        world.profile_data.save()

    runner = CliRunner(echo_stdin=True)
    # import cli after config path is set
    from clive.__private.cli.main import cli

    yield cli, runner

    init_node.close()
