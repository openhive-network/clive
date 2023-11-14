import errno
from dataclasses import dataclass
from pathlib import Path

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError, CLIWorkingAccountIsNotSetError
from clive.__private.core.commands.activate import ActivateInvalidPasswordError, WalletDoesNotExistsError
from clive.__private.core.keys import (
    KeyAliasAlreadyInUseError,
    PrivateKey,
    PrivateKeyAliased,
    PrivateKeyInvalidFormatError,
)


@dataclass(kw_only=True)
class AddKey(WorldBasedCommand):
    password: str
    key_or_path: str | Path
    """str might be a path to a file or a private key value."""

    alias: str | None = None

    @property
    def private_key_aliased(self) -> PrivateKeyAliased:
        key_or_path = Path(self.key_or_path)

        if key_or_path.is_file():
            private_key = PrivateKey.from_file(key_or_path)
        else:
            try:
                private_key = PrivateKey(value=str(self.key_or_path))
            except PrivateKeyInvalidFormatError as error:
                raise CLIPrettyError(str(error), errno.EINVAL) from None

        alias = self.alias if self.alias else private_key.calculate_public_key().value

        return private_key.with_alias(alias)

    async def _run(self) -> None:
        profile_data = self.world.profile_data
        if not profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(profile_data)

        typer.echo("Importing key...")

        try:
            profile_data.working_account.keys.add_to_import(self.private_key_aliased)
        except KeyAliasAlreadyInUseError as error:
            raise CLIPrettyError(str(error), errno.EEXIST) from None

        try:
            await self.world.commands.activate(password=self.password)
        except (ActivateInvalidPasswordError, WalletDoesNotExistsError):
            profile_data.skip_saving()
            raise

        await self.world.commands.sync_data_with_beekeeper()

        typer.echo("Key imported.")
