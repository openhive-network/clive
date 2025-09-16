from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrivateKeyInvalidFormatError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.keys import PrivateKey, PrivateKeyInvalidFormatError


@dataclass(kw_only=True)
class GeneratePublicKey(ExternalCLICommand):
    async def _run(self) -> None:
        value = self.read_interactive("Enter private key") if self.is_interactive else self.read_piped()
        try:
            private_key = PrivateKey(value=value)
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrivateKeyInvalidFormatError from error
        print_cli(private_key.calculate_public_key().value)
