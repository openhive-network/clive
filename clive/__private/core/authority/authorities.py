from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.models.aliased import Authority as SchemasAuthority


@dataclass(kw_only=True, frozen=True)
class Authority:
    weight_threshold: int
    account_auths: list[tuple[str, int]]
    key_auths: list[tuple[str, int]]

    @classmethod
    def from_schemas_authority(cls, schemas_authority: SchemasAuthority) -> Authority:
        account_auths = [(str(account_name), int(weight)) for account_name, weight in schemas_authority.account_auths]
        key_auths = [(str(key), int(weight)) for key, weight in schemas_authority.key_auths]
        return cls(
            weight_threshold=schemas_authority.weight_threshold,
            account_auths=account_auths,
            key_auths=key_auths,
        )


@dataclass(kw_only=True, frozen=True)
class AllAuthorities:
    owner: Authority
    active: Authority
    posting: Authority
    owner_lut: dict[str, Authority] = field(default_factory=dict)
    active_lut: dict[str, Authority] = field(default_factory=dict)
    posting_lut: dict[str, Authority] = field(default_factory=dict)
    last_updated: datetime
