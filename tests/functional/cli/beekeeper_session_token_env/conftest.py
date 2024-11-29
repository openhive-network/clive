from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import CLITesterWithSessionFactory, EnvContextFactory


@pytest.fixture
async def cli_tester_with_session_token_locked(
    beekeeper: Beekeeper,
    cli_tester: CLITester,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
) -> AsyncGenerator[CLITester]:
    with beekeeper_session_token_env_context_factory(beekeeper.token):
        await beekeeper.api.lock_all()
        yield cli_tester


@pytest.fixture
async def cli_tester_with_session_token_unlocked(
    beekeeper: Beekeeper,
    cli_tester_with_session_token_locked: CLITester,
) -> CLITester:
    await beekeeper.api.unlock(wallet_name=WORKING_ACCOUNT_NAME, password=WORKING_ACCOUNT_PASSWORD)
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
