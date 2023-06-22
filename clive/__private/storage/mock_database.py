from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, overload

from clive.__private.core import iwax
from clive.models import Asset

if TYPE_CHECKING:
    from pathlib import Path


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


def default_hive() -> Asset.HIVE:
    return Asset.hive(0)


def default_hbd() -> Asset.HBD:
    return Asset.hbd(0)


def default_vests() -> Asset.HIVE:
    return Asset.vests(0)


@dataclass
class Manabar:
    value: int = 0
    max_value: int = 1
    full_regeneration: timedelta = field(default_factory=timedelta)

    @property
    def percentage(self) -> float:
        assert self.max_value > 0
        return (self.value * 100.0) / self.max_value


@dataclass
class NodeData:
    hbd_savings: Asset.HBD = field(default_factory=default_hbd)
    hbd_unclaimed: Asset.HBD = field(default_factory=default_hbd)
    hive_balance: Asset.HIVE = field(default_factory=default_hive)
    hive_dollars: Asset.HBD = field(default_factory=default_hbd)
    hive_power_balance: int = 0
    hive_savings: Asset.HIVE = field(default_factory=default_hive)
    hive_unclaimed: Asset.HIVE = field(default_factory=default_hive)
    hp_unclaimed: Asset.VESTS = field(default_factory=default_vests)
    last_refresh: datetime = field(default_factory=lambda: datetime.now())
    last_transaction: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))
    recovery_account: str = ""
    reputation: int = 0
    warnings: int = 0
    rc_manabar: Manabar = field(default_factory=Manabar)
    vote_manabar: Manabar = field(default_factory=Manabar)
    downvote_manabar: Manabar = field(default_factory=Manabar)


@dataclass
class Account:
    name: str
    data: NodeData = field(default_factory=NodeData)


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
    value: str
    file_path: Path | None = None

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

    @classmethod
    def validate_key(cls, key: str) -> bool:
        try:
            cls(key).calculate_public_key()
        except iwax.WaxOperationFailedError:
            return False
        return True

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


@dataclass
class WorkingAccount(Account):
    keys: list[PublicKeyAliased] = field(default_factory=list)
    keys_to_import: dict[str, PrivateKey] = field(default_factory=dict)
