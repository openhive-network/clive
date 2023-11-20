from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from clive.__private.core.keys import PrivateKeyAliased

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from clive.__private.core.keys import PublicKeyAliased


@dataclass
class Keys:
    @dataclass
    class KeysPair:
        pub_key: PublicKeyAliased
        wif_key: PrivateKeyAliased

    def __init__(self, count: int = 0) -> None:
        self.pairs: list[Keys.KeysPair] = []
        for _ in range(count):
            self.pairs.append(self.generate_key_pair())

    def get_public_keys(self, *, sort: bool = True) -> list[str]:
        pub_keys = [pair.pub_key.value for pair in self.pairs]
        if sort:
            pub_keys.sort()
        return pub_keys

    def get_wif_keys(self, *, sort: bool = True) -> list[str]:
        wif_keys = [pair.wif_key.value for pair in self.pairs]
        if sort:
            wif_keys.sort()
        return wif_keys

    def generate_key_pair(self, *, alias: str | None = None) -> KeysPair:
        alias = f"key-{len(self.pairs)}" if alias is None else alias
        private_key = PrivateKeyAliased.create(with_alias=alias)
        public_key = private_key.calculate_public_key()

        return Keys.KeysPair(public_key, private_key)


@dataclass
class WalletInfo:
    password: str
    name: str
    keys: Keys = field(default_factory=Keys)


Wallets = list[WalletInfo]


class WalletsGeneratorT(Protocol):
    def __call__(
        self, count: int, *, import_keys: bool = True, keys_per_wallet: int = 1
    ) -> Coroutine[Any, Any, list[WalletInfo]]:
        ...
