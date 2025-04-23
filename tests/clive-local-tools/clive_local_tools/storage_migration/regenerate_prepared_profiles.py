"""
Will regenerate prepared profiles.

Profiles will be stored in current version of ProfileStorageModel.
If we are having storage in current version migration is not performed.
Use this script only if migration at some point is broken.
"""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.before_launch import _initialize_user_settings
from clive.__private.core.constants.setting_identifiers import DATA_PATH, NODE_CHAIN_ID, SECRETS_NODE_ADDRESS
from clive.__private.core.world import World
from clive.__private.models.schemas import TransferOperation
from clive.__private.settings import settings
from clive_local_tools.data.constants import TESTNET_CHAIN_ID
from clive_local_tools.testnet_block_log import run_node
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA, ALT_WORKING_ACCOUNT2_DATA

if TYPE_CHECKING:
    from collections.abc import Generator

    from clive_local_tools.data.models import AccountData


def _clear_wallet_and_profiles(path: Path) -> None:
    extensions = {".profile", ".wallet"}
    for item in path.rglob("*"):
        if item.suffix in extensions:
            item.unlink()


def _prepare_data_path(path: Path) -> None:
    _clear_wallet_and_profiles(path)
    settings.set(DATA_PATH, path)
    _initialize_user_settings()


@contextmanager
def environment(path: Path) -> Generator[tt.RawNode]:
    _prepare_data_path(path)
    node = run_node(webserver_http_endpoint="0.0.0.0:8090")
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    settings.set(NODE_CHAIN_ID, TESTNET_CHAIN_ID)
    yield node
    # it shouldn't be necessary to explicitly close node but without this program hangs forever, this might be a bug
    node.close()


async def creatre_profile_with_wallets(world: World, account_data: AccountData) -> None:
    account_name = account_data.account.name
    password = account_name * 2
    await world.create_new_profile_with_wallets(account_name, password, account_name)


async def _main() -> None:
    directory = Path(__file__).parent.absolute()

    with environment(directory / "without_alarms_and_operations"):
        async with World() as world_cm:
            await creatre_profile_with_wallets(world_cm, ALT_WORKING_ACCOUNT1_DATA)

    with environment(directory / "with_alarms"):
        async with World() as world_cm:
            await creatre_profile_with_wallets(world_cm, ALT_WORKING_ACCOUNT1_DATA)
            accounts = [world_cm.profile.accounts.working]
            await world_cm.commands.update_node_data(accounts=accounts)
            await world_cm.commands.update_alarms_data(accounts=accounts)
            all_alarms = world_cm.profile.accounts.working.alarms.all_alarms
            assert all_alarms, "Alarms should be updated and stored in profile"

    with environment(directory / "with_operations"):
        async with World() as world_cm:
            await creatre_profile_with_wallets(world_cm, ALT_WORKING_ACCOUNT1_DATA)
            world_cm.profile.add_operation(
                TransferOperation(
                    from_=ALT_WORKING_ACCOUNT1_DATA.account.name,
                    to=ALT_WORKING_ACCOUNT2_DATA.account.name,
                    amount=tt.Asset.Hive(1),
                    memo="",
                )
            )
            operations = world_cm.profile.transaction.operations
            assert operations, "There should be some operations stored in transaction"


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
