from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.keys import PrivateKey


@dataclass(kw_only=True)
class GenerateRandomKey(ExternalCLICommand):
    key_pairs: int

    async def _run(self) -> None:
        for _ in range(self.key_pairs):
            private_key = PrivateKey.create()
            print_cli(private_key.value)
            print_cli(private_key.calculate_public_key().value)
