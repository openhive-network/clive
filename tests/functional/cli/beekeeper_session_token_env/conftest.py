from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import CLITesterWithSessionFactory


@pytest.fixture
def cli_tester_with_session_token(
    cli_tester_with_session_token_locked: CLITester,
    cli_tester: CLITester,
) -> CLITesterWithSessionFactory:
    def __cli_tester_with_session(*, unlocked: bool) -> CLITester:
        if unlocked:
            return cli_tester
        return cli_tester_with_session_token_locked

    return __cli_tester_with_session
