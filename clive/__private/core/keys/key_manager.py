from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import Literal

from clive.__private.core.keys.keys import KeyAliased, PrivateKey, PrivateKeyAliased, PublicKey, PublicKeyAliased
from clive.__private.logger import logger
from clive.exceptions import CliveError

ImportCallbackT = Callable[[PrivateKeyAliased], PublicKeyAliased]


class KeyAliasAlreadyInUseError(CliveError):
    pass


class KeyNotFoundError(CliveError):
    pass


class KeyManager:
    """
    An object that manages a number of keys. A container-like object which you iterate over to see all the public keys.
    """

    def __init__(self) -> None:
        self.__keys: list[PublicKeyAliased] = []
        self.__keys_to_import: list[PrivateKeyAliased] = []

    def __iter__(self) -> Iterator[PublicKeyAliased]:
        return iter(sorted(self.__keys, key=lambda key: key.alias))

    def __reversed__(self) -> Iterator[PublicKeyAliased]:
        return iter(sorted(self.__keys, key=lambda key: key.alias, reverse=True))

    def __len__(self) -> int:
        return len(self.__keys)

    def __bool__(self) -> bool:
        return bool(self.__keys)

    def __contains__(self, key: str | PublicKey | PublicKeyAliased | PrivateKey | PrivateKeyAliased) -> bool:
        """Check if a key is in the key manager. Possible types are determined by the __eq__ of keys."""
        return key in self.__keys

    @property
    def every(self) -> list[PublicKeyAliased]:
        """A *copy* of the keys."""
        return self.__keys.copy()

    @property
    def first(self) -> PublicKeyAliased:
        return self.__keys[0]

    def is_public_alias_available(self, alias: str) -> bool:
        return self.__is_alias_available(alias, self.__keys)

    def is_key_to_import_alias_available(self, alias: str) -> bool:
        return self.__is_alias_available(alias, self.__keys_to_import)

    def get(self, alias: str) -> PublicKeyAliased:
        for key in self.__keys:
            if key.alias == alias:
                return key
        raise KeyNotFoundError(f"Key with alias `{alias}` not found.")

    def add(self, *keys: PublicKeyAliased) -> None:
        for key in keys:
            self.__assert_no_alias_conflict(key.alias, "public")
            self.__keys.append(key)

    def remove(self, *keys: PublicKeyAliased) -> None:
        """Remove a key alias from the Clive's key manager. Still remains in the beekeeper."""
        for key in keys:
            self.__keys.remove(key)

    def add_to_import(self, *keys: PrivateKeyAliased) -> None:
        for key in keys:
            self.__assert_no_alias_conflict(key.alias, "to_import")
            self.__keys_to_import.append(key)

    def set_to_import(self, keys: Sequence[PrivateKeyAliased]) -> None:
        self.__keys_to_import = list(keys)

    def import_pending_to_beekeeper(self, import_callback: ImportCallbackT) -> None:
        for key in self.__keys_to_import:
            imported = import_callback(key)
            self.add(imported)
        self.__keys_to_import.clear()
        logger.debug("Imported all pending keys to beekeeper.")

    @staticmethod
    def __is_alias_available(alias: str, keys: Sequence[KeyAliased]) -> bool:
        known_aliases = [key.alias for key in keys]
        return alias not in known_aliases

    def __assert_no_alias_conflict(self, alias: str, key_type: Literal["public", "to_import"]) -> None:
        fun: dict[str, Callable[[str], bool]] = {
            "public": self.is_public_alias_available,
            "to_import": self.is_key_to_import_alias_available,
        }

        if not fun[key_type](alias):
            raise KeyAliasAlreadyInUseError(f"Alias '{alias}' is already in use.")

    def rename(self, old_alias: str, new_alias: str) -> None:
        """Rename a key alias."""
        for key in self.__keys:
            if key.alias == old_alias:
                key.alias = new_alias
                return
        raise KeyNotFoundError(f"Key with alias '{old_alias}' not found.")
