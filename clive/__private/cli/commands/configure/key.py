from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError, CLIPrivateKeyInvalidFormatError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.formatters.humanize import humanize_validation_result
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
    alias: str | None = None
    key_or_path: str
    """str might be a path to a file or a private key value."""

    @property
    def private_key(self) -> PrivateKey:
        key_or_path = Path(self.key_or_path)

        try:
            if key_or_path.is_file():
                return PrivateKey.from_file(key_or_path)
            return PrivateKey(value=str(self.key_or_path))
        except PrivateKeyInvalidFormatError:
            raise CLIPrivateKeyInvalidFormatError from None

    @property
    def private_key_aliased(self) -> PrivateKeyAliased:
        private_key = self.private_key
        return private_key.with_alias(self.get_actual_alias(private_key))

    def get_actual_alias(self, private_key: PrivateKey | None = None) -> str:
        private_key = private_key or self.private_key
        return self.alias if self.alias else private_key.calculate_public_key().value

    async def validate_inside_context_manager(self) -> None:
        await self._validate_key_alias()
        await self._validate_private_key()
        await super().validate_inside_context_manager()

    async def _validate_key_alias(self) -> None:
        key_manager = self.profile.keys
        alias_result = PublicKeyAliasValidator(key_manager, validate_like_adding_new=True).validate(
            self.get_actual_alias()
        )

        if not alias_result.is_valid:
            raise CLIPrettyError(f"Can't add alias: {humanize_validation_result(alias_result)}", errno.EINVAL)

    async def _validate_private_key(self) -> None:
        private_key_result = PrivateKeyValidator().validate(self.private_key_aliased.value)
        if not private_key_result.is_valid:
            raise CLIPrettyError(f"Can't add key: {humanize_validation_result(private_key_result)}", errno.EINVAL)

    async def _run(self) -> None:
        print_cli("Importing key...")
        self.profile.keys.add_to_import(self.private_key_aliased)
        await self.world.commands.sync_data_with_beekeeper()
        print_cli("Key imported.")


@dataclass(kw_only=True)
class RemoveKey(WorldBasedCommand):
    alias: str
    from_beekeeper: bool = False
    """Indicates whether to remove the key from the Beekeeper as well or just the alias association from the profile."""

    async def validate_inside_context_manager(self) -> None:
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        print_cli(f"Removing a key aliased with `{self.alias}`...")
        public_key = self.profile.keys.get_from_alias(self.alias)
        self.__remove_key_association_from_the_profile(public_key)
        if self.from_beekeeper:
            await self.__remove_key_from_the_beekeeper(public_key)
        message = (
            "Key removed from the profile and the Beekeeper."
            if self.from_beekeeper
            else "Key removed from the profile."
        )
        print_cli(message)

    def __remove_key_association_from_the_profile(self, key: PublicKeyAliased) -> None:
        self.profile.keys.remove(key)

    async def __remove_key_from_the_beekeeper(self, key: PublicKeyAliased) -> None:
        await self.world.commands.remove_key(key_to_remove=key)
