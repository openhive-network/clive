from __future__ import annotations

import argparse
import shutil
import time
from random import randint
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.mock_database import Account as WatchedAccount
from clive.__private.storage.mock_database import WorkingAccount
from clive.main import main as clive_main

ARGS_COUNT = 2

if TYPE_CHECKING:
    from typing import Any

    from test_tools.__private.asset import AssetBase

engine = argparse.ArgumentParser("testnet configurator")
engine.add_argument(
    "-p",
    "--perform-onboarding",
    dest="onboarding",
    nargs="?",
    type=bool,
    const=True,
    default=False,
    help="if not set, pregenerated profile will be used, otherwise onboarding will be launched",
)
engine.add_argument(
    "-n",
    "--no-tui",
    dest="no_tui",
    nargs="?",
    type=bool,
    const=True,
    default=False,
    help="if not set, TUI will will be launched, otherwise only testnet will be configured",
)

args = engine.parse_args()
enable_onboarding: bool = args.onboarding
disable_tui: bool = args.no_tui


node = tt.InitNode()
node.config.webserver_http_endpoint = "0.0.0.0:8090"
node.config.plugin.append("account_history_rocksdb")
node.config.plugin.append("account_history_api")
node.config.plugin.append("reputation_api")
node.config.plugin.append("rc_api")
node.run()

wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
wallet.api.import_key(node.config.private_key[0])

# setup working account
creator = "initminer"
alice = tt.Account("alice")
wallet.create_account(
    alice.name, hives=tt.Asset.Test(100).as_nai(), vests=tt.Asset.Test(100).as_nai(), hbds=tt.Asset.Tbd(100).as_nai()
)

# setup watching accounts
watched_accounts = [tt.Account(name) for name in ("bob", "ocdb", "blocktrades")]


shutil.rmtree(settings.data_path, ignore_errors=True)
if not enable_onboarding:
    tt.logger.info("Configuring ProfileData for clive")

    ProfileData(
        alice.name,
        working_account=WorkingAccount(name=alice.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in watched_accounts],
    ).save()

    world = World(alice.name)
    password = CreateWallet(beekeeper=world.beekeeper, wallet=alice.name, password=alice.name).execute_with_result()
    tt.logger.info(f"password for {alice.name} is: `{password}`")
    world.profile_data.working_account.keys.add_to_import(
        PrivateKeyAliased(value=alice.private_key._value, alias=f"default {alice.name} key")
    )
    world.commands.sync_data_with_beekeeper()
    world.profile_data.save()
    world.close()


def random_assets(asset: type[AssetBase]) -> dict[str, Any]:
    return asset(randint(1_000, 5_000)).as_nai()  # type: ignore[no-any-return]


for account in watched_accounts:
    wallet.create_account(
        account.name,
        hives=random_assets(tt.Asset.Test),
        vests=random_assets(tt.Asset.Test),
        hbds=random_assets(tt.Asset.Tbd),
    )

# test
wallet.api.transfer(alice.name, creator, tt.Asset.Test(1).as_nai(), memo="memo")

node.wait_number_of_blocks(2)
tt.logger.info(f"{alice.name} public key: {alice.public_key}")
tt.logger.info(f"{alice.name} private key: {alice.private_key}")
tt.logger.info("done!")

# not passing `--no-tui` to the script will skip clive autolaunch i.e. for debugging purposes.
if not disable_tui:
    tt.logger.info("Attempting to start a clive interactive mode - exit to finish")
    clive_main()
else:
    tt.logger.info("serving forever... press Ctrl+C to exit")

    while True:
        time.sleep(1)
