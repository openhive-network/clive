from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

from clive.__private.core import iwax
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path


class PrivateKeyError(CliveError):
    """A PrivateKey related error"""


class PrivateKeyInvalidFormatError(PrivateKeyError):
    """A PrivateKey has an invalid format"""


@dataclass
class PublicKey:
    value: str

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PublicKey):
            return self.value == other.value
        if isinstance(other, PrivateKey):
            return self == other.calculate_public_key()
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def with_alias(self, alias: str) -> PublicKeyAliased:
        return PublicKeyAliased(alias=alias, value=self.value)


@dataclass
class PublicKeyAliased(PublicKey):
    alias: str

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PublicKeyAliased):
            return self.alias == other.alias and super().__eq__(other)
        return super().__eq__(other)

    def without_alias(self) -> PublicKey:
        return PublicKey(value=self.value)


@dataclass
class PrivateKey:
    """
    A container for a private key.

    Raises:
         PrivateKeyInvalidFormatError: if private key is not in valid format
    """

    value: str
    file_path: Path | None = None

    def __post_init__(self) -> None:
        self.validate(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PrivateKey):
            return self.value == other.value
        if isinstance(other, PublicKey):
            my_public_key = self.calculate_public_key()
            return my_public_key.value == other.value
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    @staticmethod
    def create() -> PrivateKey:
        return iwax.generate_private_key()

    @classmethod
    def from_file(cls, file_path: Path) -> PrivateKey:
        key = cls.read_key_from_file(file_path)
        return cls(key, file_path)

    @classmethod
    def read_key_from_file(cls, file_path: Path) -> str:
        return file_path.read_text().strip()

    @staticmethod
    def validate(key: str) -> None:
        """
        Raises:
            PrivateKeyInvalidFormatError: if private key is not in valid format
        """
        try:
            iwax.calculate_public_key(key)
        except iwax.WaxOperationFailedError:
            raise PrivateKeyInvalidFormatError() from None

    @overload
    def calculate_public_key(self) -> PublicKey:
        ...

    @overload
    def calculate_public_key(self, *, with_alias: str) -> PublicKeyAliased:
        ...

    def calculate_public_key(self, *, with_alias: str = "") -> PublicKey | PublicKeyAliased:
        public_key = iwax.calculate_public_key(self.value)

        if with_alias:
            return public_key.with_alias(with_alias)
        return public_key
