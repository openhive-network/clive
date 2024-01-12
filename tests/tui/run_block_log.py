from __future__ import annotations

import asyncio
import shutil
import sys

import test_tools as tt

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.main import _main as clive_main
from clive_local_tools.constants import TESTNET_CHAIN_ID
from clive_local_tools.tui.constants import WATCHED_PROFILES, WITNESSES_40, WORKING_PROFILES


async def prepare_profiles(node: tt.InitNode) -> None:
    tt.logger.info("Configuring ProfileData for clive")
    settings["secrets.node_address"] = f"http://{node.http_endpoint}"
    settings["node.chain_id"] = TESTNET_CHAIN_ID

    for name, watched in WATCHED_PROFILES.items():
        ProfileData(
            name,
            working_account=WorkingAccount(name=name),
            watched_accounts=[WatchedAccount(acc.name) for acc in watched],
        ).save()

    for account in WORKING_PROFILES:
        async with World(account.name) as world:
            password = await CreateWallet(
                app_state=world.app_state,
                beekeeper=world.beekeeper,
                wallet=account.name,
                password=account.name,
            ).execute_with_result()

            tt.logger.info(f"password for {account.name} is: `{password}`")
            world.profile_data.working_account.keys.add_to_import(
                PrivateKeyAliased(value=account.private_key._value, alias=f"{account.name}_key")
            )

            await world.commands.sync_data_with_beekeeper()


async def main() -> None:
    witnesses = ["initminer"]
    witnesses.extend([acc.name for acc in WITNESSES_40])

    node = tt.WitnessNode(witnesses=witnesses)
    node.config.enable_stale_production = True
    node.config.required_participation = 0
    node.config.webserver_http_endpoint = "0.0.0.0:8090"
    node.config.plugin.append("account_history_api")
    node.run(replay_from="./block_logs/testnet_block_log", wait_for_live=False)

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    for key in node.config.private_key:
        wallet.api.import_key(key)
    result = wallet.list_accounts()
    tt.logger.info(f"accounts: {result}")
    result = node.api.database.list_witnesses(start="", limit=100, order="by_name")["witnesses"]
    tt.logger.info(f"witnesses: {result}")
    history = node.api.account_history.get_account_history(account=WORKING_PROFILES[0].name, include_reversible=True)[
        "history"
    ]
    tt.logger.info(f"reversible history: {history}")
    history = node.api.account_history.get_account_history(account=WORKING_PROFILES[0].name, include_reversible=False)[
        "history"
    ]
    tt.logger.info(f"irreversible history: {history}")

    tt.logger.info(f"last block number: {node.get_last_block_number()}")

    shutil.rmtree(settings.data_path, ignore_errors=True)
    await prepare_profiles(node)

    await clive_main()

    wallet.close()
    node.close()

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
