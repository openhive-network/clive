from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest

from clive.__private.si.base import CliveSi

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

    import test_tools as tt
    from beekeepy import AsyncBeekeeper

    from clive.__private.si.base import Profile
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def clive_si(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
) -> AsyncGenerator[Profile]:
    """Will return unlocked clive script interface."""
    with ExitStack() as stack:
        address = str(beekeeper_local.http_endpoint)
        token = await (await beekeeper_local.session).token
        stack.enter_context(beekeeper_remote_address_env_context_factory(address))
        stack.enter_context(beekeeper_session_token_env_context_factory(token))
        async with CliveSi().use_unlocked_profile() as clive:
            yield clive


@pytest.fixture
async def clive_si_with_two_keys_profile(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node_two_keys_profile: tt.RawNode,  # noqa: ARG001
) -> AsyncGenerator[Profile]:
    """Will return unlocked clive script interface."""
    with ExitStack() as stack:
        address = str(beekeeper_local.http_endpoint)
        token = await (await beekeeper_local.session).token
        stack.enter_context(beekeeper_remote_address_env_context_factory(address))
        stack.enter_context(beekeeper_session_token_env_context_factory(token))
        async with CliveSi().use_unlocked_profile() as clive:
            yield clive


@pytest.fixture
def transactions_dir(tmp_path: Path) -> Path:
    """Create and return a directory for test transaction files."""
    dir_path = tmp_path / "transactions"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
