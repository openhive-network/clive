from __future__ import annotations

import pytest
import test_tools as tt
from typer.testing import CliRunner

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.core.url import Url
from clive_local_tools.cli.testing_cli import TestingCli
from clive_local_tools.data.constants import (
    CREATOR_ACCOUNT,
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_VEST_BALANCE,
)


@pytest.fixture()
async def testing_cli() -> TestingCli:
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
            cli_wallet.api.transfer(
                creator_account_name, account.name, WORKING_ACCOUNT_HIVE_LIQUID_BALANCE.as_nai(), "memo"
            )
            cli_wallet.api.transfer_to_vesting(
                creator_account_name, account.name, WORKING_ACCOUNT_VEST_BALANCE.as_nai()
            )
            cli_wallet.api.transfer(
                creator_account_name, account.name, WORKING_ACCOUNT_HBD_LIQUID_BALANCE.as_nai(), "memo"
            )

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

        await world.node.set_address(Url.parse(init_node.http_endpoint.as_string()))
        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world.commands.sync_data_with_beekeeper()

    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    runner = CliRunner()

    return TestingCli(cli, runner)
