from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, overload

from clive.__private.core import iwax

if TYPE_CHECKING:
    from pathlib import Path


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


@dataclass
class Account:
    name: str


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
    keys: list[PublicKeyAliased]
    keys_to_import: dict[str, PrivateKey]


@dataclass
class NodeData:
    reputation: float = random.uniform(0, 100)
    hive_balance: float = random.uniform(0, 100)
    hive_power_balance: float = random.uniform(0, 100)
    hive_dollars: float = random.uniform(0, 100)
    hive_savings: float = random.uniform(0, 100)
    hbd_savings: float = random.uniform(0, 100)
    hbd_unclaimed: float = random.uniform(0, 100)
    hp_unclaimed: float = random.uniform(0, 100)
    hive_unclaimed: float = random.uniform(0, 100)
    rc: int = random.randint(0, 100)
    voting_power: int = random.randint(0, 100)
    down_vote_power: int = random.randint(0, 100)

    last_refresh: datetime = datetime.now()

    def recalc(self) -> None:
        self.last_refresh: datetime = datetime.now()

        for key, value in self.__dict__.items():
            if isinstance(value, float):
                setattr(self, key, random.uniform(0, 100))
            elif isinstance(value, int):
                setattr(self, key, random.randint(0, 100))
