from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core import iwax


@dataclass(kw_only=True)
class GenerateSecretPhrase(ExternalCLICommand):
    async def _run(self) -> None:
        brain_key = iwax.suggest_brain_key()
        print_cli(brain_key)
