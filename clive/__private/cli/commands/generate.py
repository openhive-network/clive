from __future__ import annotations

from dataclasses import dataclass

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
        password = self.read_tty_mode("Enter secret phrase: ") if self.is_atty else self.read_not_tty_mode()

        private_key = iwax.generate_password_based_private_key(password, self.role, self.account_name)
        if self.only_public_key:
            typer.echo(private_key.calculate_public_key().value)
        elif self.only_private_key:
            typer.echo(private_key.value)
        else:
            typer.echo(private_key.value)
            typer.echo(private_key.calculate_public_key().value)


@dataclass(kw_only=True)
class PublicKey(ExternalCLICommand):
    async def _run(self) -> None:
        value = self.read_tty_mode("Enter private key: ") if self.is_atty else self.read_not_tty_mode()
        try:
            private_key = PrivateKey(value=value)
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrettyError(
                "Given private key has invalid format. Enter private key in wif - wallet import format "
                "(for example `5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n`)."
            ) from error
        typer.echo(private_key.calculate_public_key().value)


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
