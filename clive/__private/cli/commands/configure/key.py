from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
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
    """
    Class for adding a private key.

    Args:
        alias: An optional alias for the key. If not provided, the public key will be used as the alias.
        key_or_path: A string that can either be a path to a private key file or the private key value itself.
    """

    alias: str | None = None
    key_or_path: str
    """str might be a path to a file or a private key value."""

    @property
    def private_key(self) -> PrivateKey:
        """
        Return the private key from the provided key_or_path.

        If key_or_path is a file, it reads the private key from the file.

        If key_or_path is a string, it attempts to create a PrivateKey instance from the string.

        Raises:
            CLIPrettyError: If the key_or_path is not a valid private key format or file.

        Returns:
            PrivateKey: The private key instance.
        """
        key_or_path = Path(self.key_or_path)

        if key_or_path.is_file():
            return PrivateKey.from_file(key_or_path)

        try:
            return PrivateKey(value=str(self.key_or_path))
        except PrivateKeyInvalidFormatError as error:
            raise CLIPrettyError(str(error), errno.EINVAL) from None

    @property
    def private_key_aliased(self) -> PrivateKeyAliased:
        """
        Return the private key aliased with the actual alias.

        Returns:
            PrivateKeyAliased: The private key aliased.
        """
        private_key = self.private_key
        return private_key.with_alias(self.get_actual_alias(private_key))

    def get_actual_alias(self, private_key: PrivateKey | None = None) -> str:
        """
        Get an actual alias for the key.

        Args:
            private_key: The private key to derive the alias from. If not provided, uses the instance's private_key.

        Returns:
            str: The alias for the key, either the provided alias or the public key derived from the private key.
        """
        private_key = private_key or self.private_key
        return self.alias if self.alias else private_key.calculate_public_key().value

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the key alias and private key before adding it to the profile.

        Returns:
            None
        """
        await self._validate_key_alias()
        await self._validate_private_key()
        await super().validate_inside_context_manager()

    async def _validate_key_alias(self) -> None:
        """
        Validate the alias for the key to ensure it can be added to the profile.

        Raises:
            CLIPrettyError: If the alias is invalid or cannot be added to the profile.

        Returns:
            None
        """
        key_manager = self.profile.keys
        alias_result = PublicKeyAliasValidator(key_manager, validate_like_adding_new=True).validate(
            self.get_actual_alias()
        )

        if not alias_result.is_valid:
            raise CLIPrettyError(f"Can't add alias: {humanize_validation_result(alias_result)}", errno.EINVAL)

    async def _validate_private_key(self) -> None:
        """
        Validate the private key to ensure it is in a valid format and can be added to the profile.

        Raises:
            CLIPrettyError: If the private key is invalid or cannot be added to the profile.

        Returns:
            None
        """
        private_key_result = PrivateKeyValidator().validate(self.private_key_aliased.value)
        if not private_key_result.is_valid:
            raise CLIPrettyError(f"Can't add key: {humanize_validation_result(private_key_result)}", errno.EINVAL)

    async def _run(self) -> None:
        """
        Run the command to add the private key.

        Returns:
            None
        """
        typer.echo("Importing key...")
        self.profile.keys.add_to_import(self.private_key_aliased)
        await self.world.commands.sync_data_with_beekeeper()
        typer.echo("Key imported.")


@dataclass(kw_only=True)
class RemoveKey(WorldBasedCommand):
    """
    Class for removing a key.

    Args:
        alias: The alias of the key to be removed.
        from_beekeeper: Indicates whether to remove the key from the Beekeeper as well or just the alias association
        from the profile.
    """

    alias: str
    from_beekeeper: bool = False
    """Indicates whether to remove the key from the Beekeeper as well or just the alias association from the profile."""

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the alias of the key to ensure it exists in the profile before attempting to remove it.

        Returns:
            None
        """
        await super().validate_inside_context_manager()

    async def _run(self) -> None:
        """
        Run the command to remove the key.

        This method will remove the key from the profile and, if specified, from the Beekeeper as well.

        Returns:
            None
        """
        typer.echo(f"Removing a key aliased with `{self.alias}`...")
        public_key = self.profile.keys.get_from_alias(self.alias)
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
        """
        Remove the key from the profile.

        Args:
            key: The public key aliased to be removed from the profile.

        Returns:
            None
        """
        self.profile.keys.remove(key)

    async def __remove_key_from_the_beekeeper(self, key: PublicKeyAliased) -> None:
        """
        Remove the key from the Beekeeper.

        Args:
            key: The public key aliased to be removed from the Beekeeper.

        Returns:
            None
        """
        await self.world.commands.remove_key(key_to_remove=key)
