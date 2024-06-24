from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
from typing import Iterable

from clive.__private.core.keys.keys import KeyAliased, PrivateKey, PrivateKeyAliased, PublicKey, PublicKeyAliased
from clive.__private.logger import logger
from clive.exceptions import CliveError

ImportCallbackT = Callable[[PrivateKeyAliased], Awaitable[PublicKeyAliased]]


class KeyManagerError(CliveError):
    pass


class KeyAliasAlreadyInUseError(KeyManagerError):
    def __init__(self, alias: str) -> None:
        self.alias = alias
        self.message = f"Alias is already in use: {alias}"
        super().__init__(self.message)


class KeyNotFoundError(KeyManagerError):
    def __init__(self, alias: str | None = None) -> None:
        self.alias = alias
        self.message = f"Key with alias '{alias}' not found." if alias is not None else "Key not found."
        super().__init__(self.message)


class KeyManager:
    """A container-like object, that manages a number of keys, which you iterate over to see all the public keys."""

    def __init__(self) -> None:
        self.__keys: set[PublicKeyAliased] = set()
        self.__keys_to_import: set[PrivateKeyAliased] = set()

    def __iter__(self) -> Iterator[PublicKeyAliased]:
        return iter(self._sorted_keys())

    def __reversed__(self) -> Iterator[PublicKeyAliased]:
        return iter(self._sorted_keys(reverse=True))

    def __len__(self) -> int:
        return len(self.__keys)

    def __bool__(self) -> bool:
        return bool(self.__keys)

    def __contains__(self, key: str | PublicKey | PublicKeyAliased | PrivateKey | PrivateKeyAliased) -> bool:
        """Check if a key is in the key manager. Possible types are determined by the __eq__ of keys."""
        return key in self.__keys

    @property
    def first(self) -> PublicKeyAliased:
        try:
            return next(iter(self))
        except StopIteration as error:
            raise KeyNotFoundError from error

    def is_alias_available(self, alias: str) -> bool:
        return self._is_public_alias_available(alias) and self._is_key_to_import_alias_available(alias)

    def get(self, alias: str) -> PublicKeyAliased:
        for key in self.__keys:
            if key.alias == alias:
                return key
        raise KeyNotFoundError(alias)

    def add(self, *keys: PublicKeyAliased) -> None:
        for key in keys:
            self._assert_no_alias_conflict(key.alias)
            self.__keys.add(key)

    def remove(self, *keys: PublicKeyAliased) -> None:
        """Remove a key alias from the Clive's key manager. Still remains in the beekeeper."""
        for key in keys:
            self.__keys.remove(key)

    def rename(self, old_alias: str, new_alias: str) -> None:
        """Rename a key alias."""
        self._assert_no_alias_conflict(new_alias)

        for key in self.__keys:
            if key.alias == old_alias:
                self.__keys.remove(key)
                self.__keys.add(key.with_alias(new_alias))
                return
        raise KeyNotFoundError(old_alias)

    def add_to_import(self, *keys: PrivateKeyAliased) -> None:
        for key in keys:
            self._assert_no_alias_conflict(key.alias)
            self.__keys_to_import.add(key)

    def set_to_import(self, keys: Iterable[PrivateKeyAliased]) -> None:
        keys_to_import = list(keys)
        for key in keys_to_import:
            # since "keys to import" will be new (replaced), we should check for conflicts with the public keys only
            self._assert_no_public_alias_conflict(key.alias)
        self.__keys_to_import = set(keys_to_import)

    async def import_pending_to_beekeeper(self, import_callback: ImportCallbackT) -> None:
        imported_keys = [await import_callback(key) for key in self.__keys_to_import]
        self.__keys_to_import.clear()
        self.add(*imported_keys)
        logger.debug("Imported all pending keys to beekeeper.")

    def _sorted_keys(self, *, reverse: bool = False) -> list[PublicKeyAliased]:
        return sorted(self.__keys, key=lambda key: key.alias, reverse=reverse)

    def _is_public_alias_available(self, alias: str) -> bool:
        return self._is_alias_available(alias, self.__keys)

    def _is_key_to_import_alias_available(self, alias: str) -> bool:
        return self._is_alias_available(alias, self.__keys_to_import)

    def _is_alias_available(self, alias: str, keys: Iterable[KeyAliased]) -> bool:
        known_aliases = [key.alias for key in keys]
        return alias not in known_aliases

    def _assert_no_alias_conflict(self, alias: str) -> None:
        if not self.is_alias_available(alias):
            raise KeyAliasAlreadyInUseError(alias)

    def _assert_no_public_alias_conflict(self, alias: str) -> None:
        if not self._is_public_alias_available(alias):
            raise KeyAliasAlreadyInUseError(alias)
