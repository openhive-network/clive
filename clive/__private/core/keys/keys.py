from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, overload

from clive.__private.core import iwax
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path


class PrivateKeyError(CliveError):
    """A PrivateKey related error."""


class PrivateKeyInvalidFormatError(PrivateKeyError):
    def __init__(self, value: str) -> None:
        self.value = value
        message = f"Given key is in invalid form: `{value}`"
        super().__init__(message)


@dataclass(kw_only=True, frozen=True)
class Key(ABC):
    value: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Key):
            return self.value == other.value
        return super().__eq__(other)

    @abstractmethod
    def with_alias(self, alias: str) -> KeyAliased:
        """Return a new instance of the key with the given alias."""

    @staticmethod
    def determine_key_type(key: str) -> type[PublicKey | PrivateKey]:
        """
        Determine the type of the key from the given key raw string.

        This method requires the key to be in the correct format.
        That's because key in the wrong format will be determined as a public key also.
        """
        try:
            iwax.calculate_public_key(key)
        except iwax.WaxOperationFailedError:
            return PublicKey
        else:
            return PrivateKey


@dataclass(kw_only=True, frozen=True)
class KeyAliased(Key, ABC):
    alias: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, KeyAliased):
            return self.alias == other.alias and super().__eq__(other)
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.alias)

    @abstractmethod
    def without_alias(self) -> Key:
        """Return a new instance of the key without the alias."""


@dataclass(kw_only=True, frozen=True)
class PublicKey(Key):
    value: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PrivateKey):
            return self == other.calculate_public_key()
        if isinstance(other, str):
            return (
                self.value == other if self.determine_key_type(other) is PublicKey else self == PrivateKey(value=other)
            )
        return super().__eq__(other)

    def with_alias(self, alias: str) -> PublicKeyAliased:
        return PublicKeyAliased(alias=alias, value=self.value)


@dataclass(kw_only=True, frozen=True)
class PublicKeyAliased(KeyAliased, PublicKey):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def without_alias(self) -> PublicKey:
        return PublicKey(value=self.value)


@dataclass(kw_only=True, frozen=True)
class PrivateKey(Key):
    """
    A container for a private key.

    Raises:
    ------
     PrivateKeyInvalidFormatError: if private key is not in valid format
    """

    file_path: Path | None = None

    def __post_init__(self) -> None:
        self.validate(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PublicKey):
            return self.calculate_public_key() == other
        if isinstance(other, str):
            return self.value == other or self.calculate_public_key() == other
        return super().__eq__(other)

    @staticmethod
    @overload
    def create() -> PrivateKey: ...

    @staticmethod
    @overload
    def create(*, with_alias: str) -> PrivateKeyAliased: ...

    @staticmethod
    def create(*, with_alias: str = "") -> PrivateKey | PrivateKeyAliased:
        private_key = iwax.generate_private_key()
        return private_key.with_alias(with_alias) if with_alias else private_key

    @classmethod
    def from_file(cls, file_path: Path) -> PrivateKey:
        key = cls.read_key_from_file(file_path)
        return cls(value=key, file_path=file_path)

    @classmethod
    def read_key_from_file(cls, file_path: Path) -> str:
        return file_path.read_text().strip()

    @staticmethod
    def validate(key: str) -> None:
        """
        Validate the given key.

        Raises:
        ------
        PrivateKeyInvalidFormatError: if private key is not in valid format.
        """
        try:
            iwax.calculate_public_key(key)
        except iwax.WaxOperationFailedError:
            raise PrivateKeyInvalidFormatError(key) from None

    @classmethod
    def is_valid(cls, key: str) -> bool:
        try:
            cls.validate(key)
        except PrivateKeyInvalidFormatError:
            return False
        return True

    @overload
    def calculate_public_key(self) -> PublicKey: ...

    @overload
    def calculate_public_key(self, *, with_alias: str) -> PublicKeyAliased: ...

    def calculate_public_key(self, *, with_alias: str = "") -> PublicKey | PublicKeyAliased:
        public_key = iwax.calculate_public_key(self.value)

        if with_alias:
            return public_key.with_alias(with_alias)
        return public_key

    def with_alias(self, alias: str) -> PrivateKeyAliased:
        return PrivateKeyAliased(alias=alias, value=self.value, file_path=self.file_path)


@dataclass(kw_only=True, frozen=True)
class PrivateKeyAliased(KeyAliased, PrivateKey):
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    @overload  # type: ignore[override]
    def calculate_public_key(self, *, with_alias: Literal[False]) -> PublicKey: ...

    @overload
    def calculate_public_key(self, *, with_alias: Literal[True] = True) -> PublicKeyAliased: ...

    def calculate_public_key(self, *, with_alias: bool = True) -> PublicKey | PublicKeyAliased:
        if with_alias:
            return super().calculate_public_key(with_alias=self.alias)
        return super().calculate_public_key()

    def without_alias(self) -> PrivateKey:
        return PrivateKey(value=self.value, file_path=self.file_path)
