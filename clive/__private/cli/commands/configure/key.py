import errno
from dataclasses import dataclass
from pathlib import Path

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError, CLIWorkingAccountIsNotSetError
from clive.__private.core.commands.abc.command_secured import InvalidPasswordError
from clive.__private.core.commands.activate import ActivateInvalidPasswordError, WalletDoesNotExistsError
from clive.__private.core.keys import (
    PrivateKey,
    PrivateKeyAliased,
    PrivateKeyInvalidFormatError,
    PublicKeyAliased,
)
from clive.__private.validators.private_key_validator import PrivateKeyValidator
from clive.__private.validators.public_key_alias_validator import PublicKeyAliasValidator


@dataclass(kw_only=True)
class AddKey(WorldBasedCommand):
    password: str
    key_or_path: str | Path
    """str might be a path to a file or a private key value."""

    alias: str | None = None

    @property
    def private_key(self) -> PrivateKey:
        key_or_path = Path(self.key_or_path)

        if key_or_path.is_file():
            return PrivateKey.from_file(key_or_path)

        try:
            return PrivateKey(value=str(self.key_or_path))
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrettyError(str(error), errno.EINVAL) from None

    @property
    def private_key_aliased(self) -> PrivateKeyAliased:
        private_key = self.private_key
        return private_key.with_alias(self.get_actual_alias(private_key))

    def get_actual_alias(self, private_key: PrivateKey | None = None) -> str:
        private_key = private_key or self.private_key
        return self.alias if self.alias else private_key.calculate_public_key().value

    async def validate_inside_context_manager(self) -> None:
        profile_data = self.world.profile_data
        if not profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(profile_data)

        key_manager = profile_data.working_account.keys
        alias_result = PublicKeyAliasValidator(key_manager, validate_like_adding_new=True).validate(
            self.get_actual_alias()
        )

        if not alias_result.is_valid:
            raise CLIPrettyError(f"Can't add alias: {alias_result.failure_descriptions}", errno.EINVAL)

        private_key_result = PrivateKeyValidator().validate(self.private_key_aliased.value)
        if not private_key_result.is_valid:
            raise CLIPrettyError(f"Can't add key: {private_key_result.failure_descriptions}", errno.EINVAL)

    async def _run(self) -> None:
        profile_data = self.world.profile_data
        typer.echo("Importing key...")

        profile_data.working_account.keys.add_to_import(self.private_key_aliased)

        try:
            await self.world.commands.activate(password=self.password)
        except (ActivateInvalidPasswordError, WalletDoesNotExistsError):
            profile_data.skip_saving()
            raise

        await self.world.commands.sync_data_with_beekeeper()

        typer.echo("Key imported.")


@dataclass(kw_only=True)
class RemoveKey(WorldBasedCommand):
    alias: str
    from_beekeeper: bool = False
    """Indicates whether to remove the key from the Beekeeper as well or just the alias association from the profile."""
    password: str

    async def _run(self) -> None:
        profile_data = self.world.profile_data
        if not profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(profile_data)

        wrapper = await self.world.commands.is_password_valid(password=self.password)
        if not wrapper.result_or_raise:
            raise InvalidPasswordError

        typer.echo(f"Removing a key aliased with `{self.alias}`...")

        public_key = profile_data.working_account.keys.get(self.alias)

        self.__remove_key_association_from_the_profile(public_key)

        if self.from_beekeeper:
            await self.__remove_key_from_the_beekeeper(public_key)

        message = (
            "Key removed from the profile and the Beekeeper."
            if self.from_beekeeper
            else "Key removed from the profile."
        )
        typer.echo(message)

    def __remove_key_association_from_the_profile(self, key: PublicKeyAliased) -> None:
        self.world.profile_data.working_account.keys.remove(key)

    async def __remove_key_from_the_beekeeper(self, key: PublicKeyAliased) -> None:
        activate_wrapper = await self.world.commands.activate(password=self.password)
        activate_wrapper.raise_if_error_occurred()
        remove_wrapper = await self.world.commands.remove_key(password=self.password, key_to_remove=key)
        remove_wrapper.raise_if_error_occurred()
