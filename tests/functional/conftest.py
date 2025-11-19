from __future__ import annotations

from typing import TYPE_CHECKING

import beekeepy as bk
import pytest

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive_local_tools.data.constants import (
    KNOWN_ACCOUNT_NAMES,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
    run_node,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    import test_tools as tt
    from beekeepy import AsyncBeekeeper

    from clive.__private.core.profile import Profile
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
def logger_configuration_factory() -> Callable[[], None]:
    def _logger_configuration_factory() -> None:
        logger.setup(enable_textual=False)

    return _logger_configuration_factory


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """CLI tests are remotely connecting to a locally started beekeeper by this fixture."""
    async with await bk.AsyncBeekeeper.factory(
        settings=safe_settings.beekeeper.settings_local_factory()
    ) as beekeeper_cm:
        yield beekeeper_cm


@pytest.fixture
async def world_cli(beekeeper_local: AsyncBeekeeper) -> AsyncGenerator[World]:
    token = await (await beekeeper_local.session).token

    world = World()
    world.beekeeper_manager.settings.http_endpoint = beekeeper_local.http_endpoint
    world.beekeeper_manager.settings.use_existing_session = token
    async with world as world_cm:
        yield world_cm


@pytest.fixture
async def _prepare_profile_with_wallet_cli(world_cli: World) -> Profile:
    """Prepare profile and wallets using remote beekeeper."""
    await world_cli.create_new_profile_with_wallets(
        name=WORKING_ACCOUNT_NAME,
        password=WORKING_ACCOUNT_PASSWORD,
        working_account=WORKING_ACCOUNT_NAME,
        watched_accounts=WATCHED_ACCOUNTS_NAMES,
        known_accounts=KNOWN_ACCOUNT_NAMES,
    )
    await world_cli.commands.sync_state_with_beekeeper()
    world_cli.profile.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
    )
    await world_cli.commands.sync_data_with_beekeeper()
    await world_cli.commands.save_profile()  # required for saving imported keys aliases
    return world_cli.profile


@pytest.fixture
async def node(
    node_address_env_context_factory: EnvContextFactory, world_cli: World, _prepare_profile_with_wallet_cli: Profile
) -> AsyncGenerator[tt.RawNode]:
    node = run_node()
    await world_cli.set_address(node.http_endpoint)
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node
