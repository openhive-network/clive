from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.models.asset import Asset


@dataclass
class Balances:
    """Account balances for HBD and HIVE."""

    hbd_liquid: Asset.Hbd
    hbd_savings: Asset.Hbd
    hbd_unclaimed: Asset.Hbd
    hive_liquid: Asset.Hive
    hive_savings: Asset.Hive
    hive_unclaimed: Asset.Hive


@dataclass
class Accounts:
    """Account tracking information."""

    working_account: str | None
    tracked_accounts: list[str]
    known_accounts: list[str]


@dataclass
class Authority:
    """Authority structure for an account or key."""

    account_or_public_key: str
    weight: int


@dataclass
class AuthorityInfo:
    """Detailed authority information for an account."""

    authority_owner_account_name: str
    authority_type: str
    weight_threshold: int
    authorities: list[Authority]

@dataclass
class KeyPair:
    """Key pair (private/public)."""

    private_key: str
    public_key: str


@dataclass
class Witness:
    voted: bool
    rank: int | None
    witness_name: str
    votes: str
    created: datetime
    missed_blocks: int
    last_block: int
    price_feed: str
    version: str
