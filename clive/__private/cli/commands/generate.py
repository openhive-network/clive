from __future__ import annotations

import sys
from dataclasses import dataclass
from getpass import getpass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core import iwax
from clive.__private.core.keys import PrivateKey, PrivateKeyInvalidFormatError


@dataclass(kw_only=True)
class KeyFromSeed(ExternalCLICommand):
    account_name: str
    role: str
    only_private_key: bool
    only_public_key: bool

    async def _run(self) -> None:
        password = self._read_password_in_tty_mode() if sys.stdin.isatty() else self._read_password_in_non_tty_mode()

        private_key = iwax.generate_password_based_private_key(password, self.role, self.account_name)
        if self.only_public_key:
            typer.echo(private_key.calculate_public_key().value)
        elif self.only_private_key:
            typer.echo(private_key.value)
        else:
            keys = [private_key.calculate_public_key().value, private_key.value]
            output_string = str(keys).replace("'", '"')
            typer.echo(output_string)

    def _read_password_in_tty_mode(self) -> str:
        return getpass("Enter secret phrase: ")

    def _read_password_in_non_tty_mode(self) -> str:
        return sys.stdin.readline().rstrip()


@dataclass(kw_only=True)
class PublicKey(ExternalCLICommand):
    async def _run(self) -> None:
        value = self._read_private_key_in_tty_mode() if sys.stdin.isatty() else self._read_private_key_in_non_tty_mode()
        try:
            private_key = PrivateKey(value=value)
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrettyError("Given private key has invalid format.") from error
        typer.echo(private_key.calculate_public_key().value)

    def _read_private_key_in_tty_mode(self) -> str:
        return getpass("Enter private key: ")

    def _read_private_key_in_non_tty_mode(self) -> str:
        return sys.stdin.readline().rstrip()


@dataclass(kw_only=True)
class RandomKey(ExternalCLICommand):
    key_pairs: int

    async def _run(self) -> None:
        for _ in range(self.key_pairs):
            private_key = iwax.generate_random_private_key()
            typer.echo(private_key.value)
            typer.echo(private_key.calculate_public_key().value)


@dataclass(kw_only=True)
class SecretPhrase(ExternalCLICommand):
    async def _run(self) -> None:
        brain_key = iwax.suggest_brain_key()
        typer.echo(brain_key)
