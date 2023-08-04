from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
import time
from random import randint
from typing import TYPE_CHECKING, Final

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.main import main as clive_main

if TYPE_CHECKING:
    from collections.abc import Sequence


def init_argparse(args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clive testnet configurator")

    add = parser.add_argument

    add(
        "-p",
        "--perform-onboarding",
        nargs="?",
        type=bool,
        const=True,
        default=False,
        help="if not set, pregenerated profile will be used, otherwise clive onboarding will be launched",
    )
    add(
        "-n",
        "--no-tui",
        nargs="?",
        type=bool,
        const=True,
        default=False,
        help="if not set, TUI will will be launched, otherwise only testnet will be configured",
    )

    return parser.parse_args(args)


# ==>> WORKAROUND:
# Need to call init_argparse() before test_tools are imported, otherwise "python testnet_node.py --help"
# will display help of test_tools instead of this script.
# test_tools.__private.paths_to_executables._PathsToExecutables.parse_command_line_arguments

init_argparse(sys.argv[1:])

import test_tools as tt  # noqa: E402

CREATOR_ACCOUNT: Final[tt.Account] = tt.Account("initminer")
WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]

# <<== WORKAROUND


def prepare_node() -> tuple[tt.InitNode, tt.Wallet]:
    node = tt.InitNode()
    node.config.webserver_http_endpoint = "0.0.0.0:8090"
    node.config.plugin.append("account_history_rocksdb")
    node.config.plugin.append("account_history_api")
    node.config.plugin.append("reputation_api")
    node.config.plugin.append("rc_api")
    node.run()

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    return node, wallet


def create_working_account(wallet: tt.Wallet) -> None:
    wallet.create_account(
        WORKING_ACCOUNT.name,
        hives=tt.Asset.Test(100).as_nai(),
        vests=tt.Asset.Test(100).as_nai(),
        hbds=tt.Asset.Tbd(100).as_nai(),
    )


def create_watched_accounts(wallet: tt.Wallet) -> None:
    def random_amount() -> int:
        return randint(1_000, 5_000)

    tt.logger.info("Creating watched accounts...")
    for account in WATCHED_ACCOUNTS:
        wallet.create_account(
            account.name,
            hives=tt.Asset.Test(random_amount()).as_nai(),
            vests=tt.Asset.Test(random_amount()).as_nai(),
            hbds=tt.Asset.Tbd(random_amount()).as_nai(),
        )


async def prepare_profile() -> None:
    tt.logger.info("Configuring ProfileData for clive")

    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()

    async with World(WORKING_ACCOUNT.name) as world:
        password = await CreateWallet(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet=WORKING_ACCOUNT.name,
            password=WORKING_ACCOUNT.name,
        ).execute_with_result()

        tt.logger.info(f"password for {WORKING_ACCOUNT.name} is: `{password}`")
        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key._value, alias=f"default {WORKING_ACCOUNT.name} key")
        )
        await world.commands.sync_data_with_beekeeper()
        world.profile_data.save()


def send_test_transfer_from_working_account(wallet: tt.Wallet) -> None:
    wallet.api.transfer(WORKING_ACCOUNT.name, CREATOR_ACCOUNT.name, tt.Asset.Test(1).as_nai(), memo="memo")


def print_working_account_keys() -> None:
    tt.logger.info(f"{WORKING_ACCOUNT.name} public key: {WORKING_ACCOUNT.public_key}")
    tt.logger.info(f"{WORKING_ACCOUNT.name} private key: {WORKING_ACCOUNT.private_key}")


def launch_clive() -> None:
    tt.logger.info("Attempting to start a clive interactive mode - exit to finish")
    clive_main()


def serve_forever() -> None:
    tt.logger.info("Serving forever... press Ctrl+C to exit")

    while True:
        time.sleep(1)


async def main() -> None:
    args = init_argparse(sys.argv[1:])
    enable_clive_onboarding = args.perform_onboarding
    disable_tui = args.no_tui

    _, wallet = prepare_node()
    create_working_account(wallet)
    create_watched_accounts(wallet)
    send_test_transfer_from_working_account(wallet)
    print_working_account_keys()

    if not enable_clive_onboarding:
        shutil.rmtree(settings.data_path, ignore_errors=True)
        await prepare_profile()

    if disable_tui:
        serve_forever()
    else:
        launch_clive()


if __name__ == "__main__":
    asyncio.run(main())
