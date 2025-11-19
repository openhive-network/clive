from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.chaining.chained_command import ChainedCommand
from clive_local_tools.cli.command_options import extract_params

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.models.schemas import PublicKey
    from clive_local_tools.cli.command_options import CLIArgumentValue, CLIOptionValue


class UpdateAuthority(ChainedCommand):
    def add_key(  # noqa: PLR0913
        self,
        *,
        key: PublicKey,
        weight: int,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("add-key", cli_named_options=extract_params(locals()))
        return self

    def add_account(  # noqa: PLR0913
        self,
        *,
        account: str,
        weight: int,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("add-account", cli_named_options=extract_params(locals()))
        return self

    def remove_key(
        self,
        *,
        key: PublicKey,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("remove-key", cli_named_options=extract_params(locals()))
        return self

    def remove_account(
        self,
        *,
        account: str,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("remove-account", cli_named_options=extract_params(locals()))
        return self

    def modify_key(  # noqa: PLR0913
        self,
        *,
        key: PublicKey,
        weight: int,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("modify-key", cli_named_options=extract_params(locals()))
        return self

    def modify_account(  # noqa: PLR0913
        self,
        *,
        account: str,
        weight: int,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateAuthority:
        self._add_command_to_chain("modify-account", cli_named_options=extract_params(locals()))
        return self


class UpdateOwnerAuthority(UpdateAuthority):
    def __init__(
        self,
        typer: CliveTyper,
        runner: CliRunner,
        *,
        cli_positional_args: Iterable[CLIArgumentValue] | None = None,
        cli_named_options: Mapping[str, CLIOptionValue] | None = None,
    ) -> None:
        command = ["process", "update-owner-authority"]
        super().__init__(
            typer, runner, command, cli_positional_args=cli_positional_args, cli_named_options=cli_named_options
        )


class UpdateActiveAuthority(UpdateAuthority):
    def __init__(
        self,
        typer: CliveTyper,
        runner: CliRunner,
        *,
        cli_positional_args: Iterable[CLIArgumentValue] | None = None,
        cli_named_options: Mapping[str, CLIOptionValue] | None = None,
    ) -> None:
        command = ["process", "update-active-authority"]
        super().__init__(
            typer, runner, command, cli_positional_args=cli_positional_args, cli_named_options=cli_named_options
        )


class UpdatePostingAuthority(UpdateAuthority):
    def __init__(
        self,
        typer: CliveTyper,
        runner: CliRunner,
        *,
        cli_positional_args: Iterable[CLIArgumentValue] | None = None,
        cli_named_options: Mapping[str, CLIOptionValue] | None = None,
    ) -> None:
        command = ["process", "update-posting-authority"]
        super().__init__(
            typer, runner, command, cli_positional_args=cli_positional_args, cli_named_options=cli_named_options
        )
