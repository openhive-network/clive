from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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
class NodeData:
    reputation: int = 0
    hive_balance: Asset.HIVE = field(default_factory=default_hive)
    hive_dollars: Asset.HBD = field(default_factory=default_hbd)
    hive_savings: Asset.HIVE = field(default_factory=default_hive)
    hbd_savings: Asset.HBD = field(default_factory=default_hbd)
    hive_unclaimed: Asset.HIVE = field(default_factory=default_hive)
    hbd_unclaimed: Asset.HBD = field(default_factory=default_hbd)
    hp_unclaimed: Asset.VESTS = field(default_factory=default_vests)
    voting_power: int = 0
    down_vote_power: int = 0
    rc: int = 0
    hive_power_balance: int = 0
    hours_until_full_refresh_voting_power: int = 0
    hours_until_full_refresh_downvoting_power: int = 0
    hours_until_full_refresh_rc: int = 0
    last_refresh: datetime = datetime.now()


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
