from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_no_exit_code_error,
    assert_weight_threshold,
)
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


weight_threshold = 12
other_account = WATCHED_ACCOUNTS[0]
weight = 323
modified_weight = 324


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold_offline(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "--force-offline",
            f"--threshold={weight_threshold}",
            "add-account",
            f"--account={WORKING_ACCOUNT.name}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_weight_threshold(runner, cli, authority, weight_threshold)
    assert_is_authority(runner, cli, WORKING_ACCOUNT.name, authority)
    assert_authority_weight(runner, cli, WORKING_ACCOUNT.name, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_account_offline(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "--force-offline",
            "add-account",
            f"--account={other_account.name}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_authority(runner, cli, other_account.name, authority)
    assert_authority_weight(runner, cli, other_account.name, authority, weight)
    assert_is_not_authority(runner, cli, WORKING_ACCOUNT.name, authority)
    assert_is_not_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key_offline(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "--force-offline",
            "add-key",
            f"--key={WORKING_ACCOUNT.public_key}",
            f"--weight={weight}",
            "modify-key",
            f"--key={WORKING_ACCOUNT.public_key}",
            f"--weight={modified_weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)
    assert_authority_weight(runner, cli, WORKING_ACCOUNT.public_key, authority, modified_weight)
