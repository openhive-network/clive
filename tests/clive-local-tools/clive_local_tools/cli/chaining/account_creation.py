from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.chaining.chained_command import ChainedCommand
from clive_local_tools.cli.command_options import extract_params

if TYPE_CHECKING:
    from pathlib import Path

    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.models.schemas import PublicKey
    from clive_local_tools.cli.command_options import CliOptionT


class AccountCreation(ChainedCommand):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **cli_options: CliOptionT) -> None:
        command = ["process", "account-creation"]
        super().__init__(typer, runner, command, **cli_options)

    def owner(  # noqa: PLR0913
        self,
        *,
        key: str | PublicKey | list[str | PublicKey] | None = None,
        account: str | list[str] | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> AccountCreation:
        self._add_command_to_chain("owner", **extract_params(locals()))
        return self

    def active(  # noqa: PLR0913
        self,
        *,
        key: str | PublicKey | list[str | PublicKey] | None = None,
        account: str | list[str] | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> AccountCreation:
        self._add_command_to_chain("active", **extract_params(locals()))
        return self

    def posting(  # noqa: PLR0913
        self,
        *,
        key: str | PublicKey | list[str | PublicKey] | None = None,
        account: str | list[str] | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> AccountCreation:
        self._add_command_to_chain("posting", **extract_params(locals()))
        return self

    def memo(
        self,
        *,
        key: PublicKey,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> AccountCreation:
        self._add_command_to_chain("memo", **extract_params(locals()))
        return self
