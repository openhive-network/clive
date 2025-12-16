from __future__ import annotations

from clive.__private.core.keys.keys import PrivateKey
from clive.__private.py.data_classes import KeyPair
from clive.__private.py.foundation.base import CommandBase
from clive.__private.py.validators import (
    KeyPairsNumberValidator,
)


class GenerateRandomKey(CommandBase[list[KeyPair]]):
    def __init__(self, key_pairs: int) -> None:
        self.key_pairs = key_pairs

    async def validate(self) -> None:
        KeyPairsNumberValidator().validate(self.key_pairs)

    async def _run(self) -> list[KeyPair]:
        key_pairs_list = []
        for _ in range(self.key_pairs):
            private_key = PrivateKey.generate()
            public_key = private_key.calculate_public_key()
            key_pairs_list.append(KeyPair(private_key=private_key.value, public_key=public_key.value))
        return key_pairs_list
