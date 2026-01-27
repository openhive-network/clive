from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import align_to_dot, humanize_asset
from clive.exceptions import RequestIdError

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.asset import Asset
    from schemas.apis.database_api import FindEscrows
    from schemas.apis.database_api.fundaments_of_reponses import EscrowsFundament


@dataclass
class HarvestedDataRaw:
    escrows: FindEscrows | None = None


@dataclass
class SanitizedData:
    escrows: list[EscrowsFundament]


@dataclass
class EscrowInfo:
    """Processed escrow information with status."""

    id_: int
    escrow_id: int
    from_: str
    to: str
    agent: str
    ratification_deadline: datetime
    escrow_expiration: datetime
    hbd_balance: Asset.Hbd
    hive_balance: Asset.Hive
    pending_fee: Asset.LiquidT
    to_approved: bool
    agent_approved: bool
    disputed: bool

    @property
    def status(self) -> str:
        """Return the status of the escrow."""
        if self.disputed:
            return "disputed"
        if self.to_approved and self.agent_approved:
            return "approved"
        return "pending"


@dataclass
class EscrowData:
    escrows: list[EscrowInfo]

    def get_escrow_by_id(self, escrow_id: int) -> EscrowInfo | None:
        """Find escrow by its ID."""
        for escrow in self.escrows:
            if escrow.escrow_id == escrow_id:
                return escrow
        return None

    def create_escrow_id(self, *, future_escrow_ids: list[int] | None = None) -> int:
        """
        Calculate the next available escrow id for EscrowTransferOperation.

        Args:
            future_escrow_ids: Future escrow ids to include in calculation. (e.g. already stored in the cart)

        Raises:
            RequestIdError: If the maximum number of escrow ids is exceeded.

        Returns:
            The next available escrow id.
        """
        max_number_of_escrow_ids: Final[int] = 100

        future_escrow_ids = future_escrow_ids or []
        existing_ids = [e.escrow_id for e in self.escrows]
        all_ids = existing_ids + future_escrow_ids
        if not all_ids:
            return 0

        if len(all_ids) >= max_number_of_escrow_ids:
            raise RequestIdError("Maximum quantity of escrow ids is 100")

        last_occupied_id = max(all_ids)
        return last_occupied_id + 1

    def get_aligned_hbd_amounts(self) -> list[str]:
        """Return dot-aligned HBD amounts of escrows."""
        amounts_to_align = [f"{humanize_asset(e.hbd_balance)}" for e in self.escrows]
        return align_to_dot(*amounts_to_align)

    def get_aligned_hive_amounts(self) -> list[str]:
        """Return dot-aligned HIVE amounts of escrows."""
        amounts_to_align = [f"{humanize_asset(e.hive_balance)}" for e in self.escrows]
        return align_to_dot(*amounts_to_align)


@dataclass(kw_only=True)
class EscrowDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, EscrowData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.find_escrows(from_=self.account_name),
            )
        raise bke.UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            escrows=self.__assert_escrows(data.escrows),
        )

    async def _process_data(self, data: SanitizedData) -> EscrowData:
        escrows = [
            EscrowInfo(
                id_=e.id_,
                escrow_id=e.escrow_id,
                from_=e.from_,
                to=e.to,
                agent=e.agent,
                ratification_deadline=e.ratification_deadline,
                escrow_expiration=e.escrow_expiration,
                hbd_balance=e.hbd_balance,
                hive_balance=e.hive_balance,
                pending_fee=e.pending_fee,
                to_approved=e.to_approved,
                agent_approved=e.agent_approved,
                disputed=e.disputed,
            )
            for e in data.escrows
        ]
        return EscrowData(escrows=escrows)

    def __assert_escrows(self, data: FindEscrows | None) -> list[EscrowsFundament]:
        assert data is not None, "FindEscrows data is missing"
        return data.escrows
