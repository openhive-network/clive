from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME
from clive_local_tools.tui.utils import unlock_wallet

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from beekeepy import AsyncBeekeeper

    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import CLITesterWithSessionFactory, EnvContextFactory


@pytest.fixture
async def cli_tester_with_session_token_locked(
    beekeeper: AsyncBeekeeper,
    cli_tester: CLITester,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
) -> AsyncGenerator[CLITester]:
    session = await beekeeper.session
    with beekeeper_session_token_env_context_factory(await session.token):
        await session.lock_all()
        yield cli_tester


@pytest.fixture
async def cli_tester_with_session_token_unlocked(
    beekeeper: AsyncBeekeeper,
    cli_tester_with_session_token_locked: CLITester,
) -> CLITester:
    await unlock_wallet(beekeeper, WORKING_ACCOUNT_NAME, WORKING_ACCOUNT_PASSWORD)
    return cli_tester_with_session_token_locked


@pytest.fixture
def cli_tester_with_session_token(
    cli_tester_with_session_token_locked: CLITester,
    cli_tester_with_session_token_unlocked: CLITester,
) -> CLITesterWithSessionFactory:
    def __cli_tester_with_session(*, unlocked: bool) -> CLITester:
        if unlocked:
            return cli_tester_with_session_token_unlocked
        return cli_tester_with_session_token_locked

    return __cli_tester_with_session
