from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import Result

    from clive_local_tools.cli.testing_cli import TestingCli


def balances(testing_cli: TestingCli, profile_name: str | None = None, account_name: str | None = None) -> Result:
    """If profile_name or account_name is None then default value is used."""
    return testing_cli.show_balances(profile_name=profile_name, account_name=account_name)
