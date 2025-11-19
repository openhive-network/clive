from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.si.base import UnlockedCliveSi
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    import test_tools as tt
    from beekeepy import AsyncBeekeeper

    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def _prepare_profile_with_wallet_cli_two_keys(
    prepare_profile_with_wallet_cli: Profile,  # noqa: ARG001
    world_cli: World,
) -> Profile:
    """Add second key to prepared profile in previous fixture."""
    world_cli.profile.keys.add_to_import(
        PrivateKeyAliased(
            value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
        )
    )
    await world_cli.commands.sync_data_with_beekeeper()
    await world_cli.commands.save_profile()  # required for saving imported keys aliases
    return world_cli.profile


@pytest.fixture
async def clive_si(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
) -> AsyncGenerator[UnlockedCliveSi]:
    """Will return unlocked clive script interface."""
    with ExitStack() as stack:
        address = str(beekeeper_local.http_endpoint)
        token = await (await beekeeper_local.session).token
        stack.enter_context(beekeeper_remote_address_env_context_factory(address))
        stack.enter_context(beekeeper_session_token_env_context_factory(token))
        async with UnlockedCliveSi() as clive:
            yield clive


@pytest.fixture
async def clive_si_with_two_keys_profile(
    _prepare_profile_with_wallet_cli_two_keys: Profile,
    clive_si: UnlockedCliveSi,
) -> UnlockedCliveSi:
    """Will return unlocked clive script interface."""
    return clive_si
