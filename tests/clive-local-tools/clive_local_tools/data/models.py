from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import test_tools as tt

from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased


@dataclass
class Keys:
    @dataclass
    class KeysPair:
        public_key: PublicKeyAliased
        private_key: PrivateKeyAliased

    def __init__(self, count: int = 0) -> None:
        self.pairs: list[Keys.KeysPair] = []
        for _ in range(count):
            self.pairs.append(self.generate_key_pair())

    def get_public_keys(self, *, sort: bool = True) -> list[str]:
        pub_keys = [pair.public_key.value for pair in self.pairs]
        if sort:
            pub_keys.sort()
        return pub_keys

    def get_private_keys(self, *, sort: bool = True) -> list[str]:
        private_keys = [pair.private_key.value for pair in self.pairs]
        if sort:
            private_keys.sort()
        return private_keys

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
    keys_from_file: Path | None = None

    def __post_init__(self) -> None:
        if self.keys_from_file:
            self.load_keys_from_file(self.keys_from_file)

    def load_keys_from_file(self, keys_from_file: Path) -> None:
        """Load keys from given path."""
        with Path.open(keys_from_file) as key_file:
            keys = json.load(key_file)
            if keys_from_file.name.endswith("alias.keys"):
                for alias, wif_key in keys.items():
                    pv = PrivateKeyAliased(value=wif_key, alias=alias)
                    self.keys.pairs.append(Keys.KeysPair(pv.calculate_public_key(), pv))
            else:
                for nr, key in enumerate(keys):
                    self.keys.pairs.append(
                        Keys.KeysPair(
                            PublicKeyAliased(value=key["public_key"], alias=f"key-{nr}"),
                            PrivateKeyAliased(value=key["private_key"], alias=f"key-{nr}"),
                        )
                    )
            self.keys_from_file = keys_from_file

    @property
    def public_key(self) -> PublicKeyAliased:
        """Return the first key in the wallet."""
        return self.key_pair.public_key

    @property
    def private_key(self) -> PrivateKeyAliased:
        """Return the first key in the wallet."""
        return self.key_pair.private_key

    @property
    def key_pair(self) -> Keys.KeysPair:
        """Return the first key pair in the wallet."""
        return self.keys.pairs[0]


@dataclass
class AccountData:
    account: tt.Account
    hives_liquid: tt.Asset.TestT
    hbds_liquid: tt.Asset.TbdT
    vests: tt.Asset.TestT  # in hive power
    hives_savings: tt.Asset.TestT = field(default_factory=lambda: tt.Asset.Test(0))
    hbds_savings: tt.Asset.TbdT = field(default_factory=lambda: tt.Asset.Tbd(0))
    hives_savings_withdrawal: tt.Asset.TestT = field(default_factory=lambda: tt.Asset.Test(0))
    hbds_savings_withdrawal: tt.Asset.TbdT = field(default_factory=lambda: tt.Asset.Tbd(0))

    @property
    def from_savings_transfer_count(self) -> int:
        return sum([self.hives_savings_withdrawal > 0, self.hbds_savings_withdrawal > 0])
