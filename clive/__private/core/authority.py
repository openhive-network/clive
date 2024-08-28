from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from clive.__private.core.keys import PublicKey
from clive.__private.core.types import AuthorityType

if TYPE_CHECKING:
    from clive.__private.models.schemas import Authority as SchemasAuthority


@dataclass(kw_only=True, frozen=True)
class KeyWeight:
    public_key: PublicKey
    weight: int


@dataclass(kw_only=True, frozen=True)
class AuthorityWeight:
    account: str
    role: AuthorityType
    weight: int


@dataclass(kw_only=True, frozen=True)
class AccountAuthority:
    account: str
    role: AuthorityType
    key_weights: set[KeyWeight] = field(default_factory=set)
    authority_weights: set[AuthorityWeight] = field(default_factory=set)
    required_total_weight: int

    @classmethod
    def from_schemas_authority(
        cls, schemas_authority: SchemasAuthority, account_name: str, role: AuthorityType
    ) -> AccountAuthority:
        key_weights = [
            KeyWeight(public_key=PublicKey(value=str(key)), weight=int(weight))
            for key, weight in schemas_authority.key_auths
        ]
        authority_weights = [
            AuthorityWeight(public_key=PublicKey(value=str(key)), weight=int(weight), role=role)
            for key, weight in schemas_authority.key_auths
        ]
        authority_weights = [
            (str(account_name), int(weight)) for account_name, weight in schemas_authority.account_auths
        ]
        return cls(
            account=account_name,
            role=role,
            key_weights=key_weights,
            authority_weights=authority_weights,
            required_total_weight=schemas_authority.weight_threshold,
        )


@dataclass(kw_only=True, frozen=True)
class AuthoritiesCache:
    authorities_this_account: set[AccountAuthority]
    authorities_lut: set[AccountAuthority]
    last_updated: datetime