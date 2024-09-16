from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import CLITesterWithSessionT, SessionTokenContextT


@pytest.fixture
async def cli_tester_with_session_token_locked(
    world: World,
    cli_tester: CLITester,
    session_token_context: SessionTokenContextT,
) -> AsyncGenerator[CLITester]:
    async with world as world_cm:
        with session_token_context(world_cm.beekeeper.token):
            yield cli_tester


@pytest.fixture
async def cli_tester_with_session_token_unlocked(
    world: World,
    cli_tester_with_session_token_locked: CLITester,
) -> AsyncGenerator[CLITester]:
    async with world as world_cm:
        await world_cm.beekeeper.api.unlock(wallet_name=WORKING_ACCOUNT_NAME, password=WORKING_ACCOUNT_PASSWORD)
        yield cli_tester_with_session_token_locked


@pytest.fixture
def cli_tester_with_session(
    cli_tester_with_session_token_locked: CLITester,
    cli_tester_with_session_token_unlocked: CLITester,
) -> CLITesterWithSessionT:
    def __cli_tester_with_session(*, unlocked: bool) -> CLITester:
        if unlocked:
            return cli_tester_with_session_token_unlocked
        return cli_tester_with_session_token_locked

    return __cli_tester_with_session
