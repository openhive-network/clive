from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


def balances(
    runner: CliRunner, cli: CliveTyper, profile_name: str | None = None, account_name: str | None = None
) -> Result:
    """If profile_name or account_name is None then default value is used."""
    command = ["show", "balances"]
    if profile_name is not None:
        command.append(f"--profile-name={profile_name}")
    if account_name is not None:
        command.append(f"--account-name={account_name}")

    tt.logger.info(f"executing command {command}")
    return runner.invoke(cli, command)
