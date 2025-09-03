from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIMutuallyExclusiveOptionsError, CLIPrettyError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core import iwax
from clive.__private.core.keys import PrivateKey, PrivateKeyInvalidFormatError

if TYPE_CHECKING:
    from clive.__private.core.authority.types import AuthorityLevel


@dataclass(kw_only=True)
class GenerateKeyFromSeed(ExternalCLICommand):
    account_name: str
    role: AuthorityLevel
    only_private_key: bool
    only_public_key: bool

    async def validate(self) -> None:
        if self.only_private_key and self.only_public_key:
            raise CLIMutuallyExclusiveOptionsError("--only-private-key", "--only-public-key")
        await super().validate()

    async def _run(self) -> None:
        password = (
            self.read_interactive("Enter seed (like as secret phrase): ") if self.is_interactive else self.read_piped()
        )

        private_key = iwax.generate_password_based_private_key(password, self.role, self.account_name)
        if self.only_public_key:
            print_cli(private_key.calculate_public_key().value)
        elif self.only_private_key:
            print_cli(private_key.value)
        else:
            print_cli(private_key.value)
            print_cli(private_key.calculate_public_key().value)


@dataclass(kw_only=True)
class GeneratePublicKey(ExternalCLICommand):
    async def _run(self) -> None:
        value = self.read_interactive("Enter private key: ") if self.is_interactive else self.read_piped()
        try:
            private_key = PrivateKey(value=value)
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrettyError(
                "Given private key has invalid format. Enter private key in wif - wallet import format "
                "(look at `clive generate random-key` to display example)."
            ) from error
        print_cli(private_key.calculate_public_key().value)


@dataclass(kw_only=True)
class GenerateRandomKey(ExternalCLICommand):
    key_pairs: int

    async def _run(self) -> None:
        for _ in range(self.key_pairs):
            private_key = PrivateKey.create()
            print_cli(private_key.value)
            print_cli(private_key.calculate_public_key().value)


@dataclass(kw_only=True)
class GenerateSecretPhrase(ExternalCLICommand):
    async def _run(self) -> None:
        brain_key = iwax.suggest_brain_key()
        print_cli(brain_key)
