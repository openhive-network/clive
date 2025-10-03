from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.si.core.base import CommandBaseSync

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevel
from clive.__private.si.data_classes import KeyPair


class GenerateRandomKey(CommandBaseSync[list[KeyPair]]):
    def __init__(self, key_pairs: int) -> None:
        self.key_pairs = key_pairs

    def _run(self) -> list[KeyPair]:
        key_pairs_list = []
        for _ in range(self.key_pairs):
            private_key = PrivateKey.create()
            public_key = private_key.calculate_public_key()
            key_pairs_list.append(KeyPair(private_key=private_key.value, public_key=public_key.value))
        return key_pairs_list


class GenerateKeyFromSeed(CommandBaseSync[KeyPair]):
    def __init__(
        self,
        account_name: str,
        password: str,
        role: AuthorityLevel,
        *,
        only_private_key: bool,
        only_public_key: bool,
    ) -> None:
        self.account_name = account_name
        self.password = password
        self.role = role
        self.only_private_key = only_private_key
        self.only_public_key = only_public_key

    def _run(self) -> KeyPair:
        private_key = PrivateKey.create_from_seed(seed=self.password, account_name=self.account_name, role=self.role)
        public_key = private_key.calculate_public_key()
        return KeyPair(private_key=private_key.value, public_key=public_key.value)


class GeneratePublicKey(CommandBaseSync[str]):
    def __init__(self, private_key: str) -> None:
        self.private_key = private_key

    def _run(self) -> str:
        private_key = PrivateKey(value=self.private_key)
        return private_key.calculate_public_key().value


class GenerateSecretPhrase(CommandBaseSync[str]):
    def _run(self) -> str:
        return iwax.suggest_brain_key()
