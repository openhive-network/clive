from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_no_exit_code_error

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_account(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_account()

    # ASSERT
    assert_no_exit_code_error(result)
