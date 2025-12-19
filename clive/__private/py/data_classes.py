from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.models.asset import Asset


AuthorityType = Literal["owner", "active", "posting"]


@dataclass(frozen=True)
class Balances:
    """Account balances for HBD and HIVE."""

    hbd_liquid: Asset.Hbd
    hbd_savings: Asset.Hbd
    hbd_unclaimed: Asset.Hbd
    hive_liquid: Asset.Hive
    hive_savings: Asset.Hive
    hive_unclaimed: Asset.Hive

    def __str__(self) -> str:
        return (
            f"HBD: {self.hbd_liquid.pretty_amount()} (liquid), "
            f"{self.hbd_savings.pretty_amount()} (savings), "
            f"{self.hbd_unclaimed.pretty_amount()} (unclaimed) | "
            f"HIVE: {self.hive_liquid.pretty_amount()} (liquid), "
            f"{self.hive_savings.pretty_amount()} (savings), "
            f"{self.hive_unclaimed.pretty_amount()} (unclaimed)"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert balances to dictionary with legacy asset format."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        return {
            "hbd_liquid": Asset.to_legacy(self.hbd_liquid),
            "hbd_savings": Asset.to_legacy(self.hbd_savings),
            "hbd_unclaimed": Asset.to_legacy(self.hbd_unclaimed),
            "hive_liquid": Asset.to_legacy(self.hive_liquid),
            "hive_savings": Asset.to_legacy(self.hive_savings),
            "hive_unclaimed": Asset.to_legacy(self.hive_unclaimed),
        }


@dataclass(frozen=True)
class Accounts:
    """Account tracking information."""

    working_account: str | None
    tracked_accounts: tuple[str, ...]
    known_accounts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert accounts to dictionary."""
        return {
            "working_account": self.working_account,
            "tracked_accounts": list(self.tracked_accounts),
            "known_accounts": list(self.known_accounts),
        }


@dataclass(frozen=True)
class Authority:
    """Authority structure for an account or key."""

    account_or_public_key: str
    weight: int


@dataclass(frozen=True)
class AuthorityInfo:
    """Detailed authority information for an account."""

    authority_owner_account_name: str
    authority_type: AuthorityType
    weight_threshold: int
    authorities: tuple[Authority, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert authority info to dictionary."""
        return {
            "authority_owner_account_name": self.authority_owner_account_name,
            "authority_type": self.authority_type,
            "weight_threshold": self.weight_threshold,
            "authorities": [
                {"account_or_public_key": auth.account_or_public_key, "weight": auth.weight}
                for auth in self.authorities
            ],
        }


@dataclass(frozen=True)
class KeyPair:
    """Key pair (private/public)."""

    private_key: str
    public_key: str

    def __repr__(self) -> str:
        return f"KeyPair(private_key=<redacted>, public_key={self.public_key!r})"

    def __str__(self) -> str:
        return f"KeyPair(public={self.public_key[:20]}...)"

    def to_dict(self) -> dict[str, Any]:
        """Convert key pair to dictionary (private key is redacted)."""
        return {
            "private_key": "<redacted>",
            "public_key": self.public_key,
        }


@dataclass(frozen=True)
class Witness:
    """
    Witness data from the blockchain.

    Attributes:
        voted: Whether the account has voted for this witness.
        rank: Witness rank (None if not in top witnesses).
        witness_name: The witness account name.
        votes: Raw vote count (vests).
        votes_display: Human-readable vote count (e.g., "1.23M HP").
        url: Witness URL/website.
        created: When the witness was created.
        missed_blocks: Number of blocks missed by this witness.
        last_block: Last block produced by this witness.
        price_feed: Current price feed from this witness.
        version: Witness node version.
    """

    voted: bool
    rank: int | None
    witness_name: str
    votes: int
    votes_display: str
    url: str
    created: datetime
    missed_blocks: int
    last_block: int
    price_feed: str
    version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert witness to dictionary."""
        return {
            "voted": self.voted,
            "rank": self.rank,
            "witness_name": self.witness_name,
            "votes": self.votes,
            "votes_display": self.votes_display,
            "created": self.created.isoformat(),
            "missed_blocks": self.missed_blocks,
            "last_block": self.last_block,
            "price_feed": self.price_feed,
            "version": self.version,
        }


@dataclass(frozen=True)
class WitnessesResult:
    """Result of witnesses query including pagination metadata."""

    witnesses: tuple[Witness, ...]
    total_count: int
    proxy: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert witnesses result to dictionary."""
        return {
            "witnesses": [w.to_dict() for w in self.witnesses],
            "total_count": self.total_count,
            "proxy": self.proxy,
        }
