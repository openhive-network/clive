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


other_account = WATCHED_ACCOUNTS[0]
other_account2 = WATCHED_ACCOUNTS[1]
weight = 213
modified_weight = 214
weight_threshold = 2


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
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
            f"--threshold={weight_threshold}",
            "add-account",
            f"--account={other_account.name}",
            f"--weight={weight}",
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_weight_threshold(runner, cli, authority, weight_threshold)
    assert_is_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(runner, cli, other_account.name, authority)
    assert_is_authority(runner, cli, other_account.public_key, authority)
    assert_authority_weight(runner, cli, other_account.name, authority, weight)
    assert_authority_weight(runner, cli, other_account.public_key, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining2(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
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
            f"--threshold={weight_threshold}",
            "add-account",
            f"--account={other_account.name}",
            f"--weight={weight}",
            "add-account",
            f"--account={other_account2.name}",
            f"--weight={weight}",
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
            "remove-key",
            f"--key={WORKING_ACCOUNT.public_key}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_weight_threshold(runner, cli, authority, weight_threshold)
    assert_is_authority(runner, cli, other_account.name, authority)
    assert_is_authority(runner, cli, other_account2.name, authority)
    assert_is_authority(runner, cli, other_account.public_key, authority)
    assert_authority_weight(runner, cli, other_account2.name, authority, weight)
    assert_authority_weight(runner, cli, other_account.public_key, authority, weight)
    assert_is_not_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining3(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
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
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
            "add-account",
            f"--account={other_account.name}",
            f"--weight={weight}",
            "modify-key",
            f"--key={WORKING_ACCOUNT.public_key}",
            f"--weight={modified_weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(runner, cli, other_account.public_key, authority)
    assert_is_authority(runner, cli, other_account.name, authority)
    assert_authority_weight(runner, cli, WORKING_ACCOUNT.public_key, authority, modified_weight)
    assert_authority_weight(runner, cli, other_account.public_key, authority, weight)
    assert_authority_weight(runner, cli, other_account.name, authority, weight)
