from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence

from clive.__private.core.keys.keys import PrivateKey, PrivateKeyAliased, PublicKey, PublicKeyAliased

ImportCallbackT = Callable[[PrivateKeyAliased], PublicKeyAliased]


class KeyManager:
    """
    An object that manages a number of keys. A container-like object which you iterate over to see all the public keys.
    """

    def __init__(self) -> None:
        self.__keys: list[PublicKeyAliased] = []
        self.__keys_to_import: list[PrivateKeyAliased] = []

    def __iter__(self) -> Iterator[PublicKeyAliased]:
        return iter(self.__keys)

    def __reversed__(self) -> Iterator[PublicKeyAliased]:
        return iter(reversed(self.__keys))

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

    def add(self, *keys: PublicKeyAliased) -> None:
        self.__keys.extend(keys)

    def remove(self, *keys: PublicKeyAliased) -> None:
        """Remove a key alias from the Clive's key manager. Still remains in the beekeeper."""
        for key in keys:
            self.__keys.remove(key)

    def add_to_import(self, *keys: PrivateKeyAliased) -> None:
        self.__keys_to_import.extend(keys)

    def set_to_import(self, keys: Sequence[PrivateKeyAliased]) -> None:
        self.__keys_to_import = list(keys)

    def import_pending_to_beekeeper(self, import_callback: ImportCallbackT) -> None:
        for key in self.__keys_to_import:
            imported = import_callback(key)
            self.add(imported)
        self.__keys_to_import.clear()
