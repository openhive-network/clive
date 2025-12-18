from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.py.base import clive_use_unlocked_profile

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from beekeepy import AsyncBeekeeper

    from clive.__private.py.base import UnlockedClivePy
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def unlocked_clive_py(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    _prepare_profile_and_setup_wallet: None,  # Profile is created and unlocked here
    node: None,  # noqa: ARG001 - Required to ensure node is running for blockchain operations
) -> AsyncGenerator[UnlockedClivePy]:
    """Create an UnlockedClivePy instance with test PyWorld and running node.

    The node fixture ensures a test node is running for blockchain operations.
    Even if some tests don't directly use the node, having it as a dependency
    here simplifies the test structure.

    Beekeeper configuration is provided via environment variables, which are
    automatically picked up by the settings system during UnlockedClivePy setup.
    """
    address = str(beekeeper_local.http_endpoint)
    token = await (await beekeeper_local.session).token

    with (
        beekeeper_remote_address_env_context_factory(address),
        beekeeper_session_token_env_context_factory(token),
    ):
        async with clive_use_unlocked_profile() as py:
            yield py
