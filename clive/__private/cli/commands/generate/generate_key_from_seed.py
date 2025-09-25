from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.keys import PrivateKey

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevel


@dataclass(kw_only=True)
class GenerateKeyFromSeed(ExternalCLICommand):
    account_name: str
    role: AuthorityLevel
    only_private_key: bool
    only_public_key: bool

    async def validate(self) -> None:
        self._validate_mutually_exclusive(only_private_key=self.only_private_key, only_public_key=self.only_public_key)
        await super().validate()

    async def _run(self) -> None:
        password = (
            self.read_interactive("Enter seed (like as secret phrase)") if self.is_interactive else self.read_piped()
        )

        private_key = PrivateKey.create_from_seed(password, self.account_name, role=self.role)
        if self.only_public_key:
            print_cli(private_key.calculate_public_key().value)
        elif self.only_private_key:
            print_cli(private_key.value)
        else:
            print_cli(private_key.value)
            print_cli(private_key.calculate_public_key().value)
