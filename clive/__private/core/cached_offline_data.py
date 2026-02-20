from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from clive.__private.models.asset import Asset
from clive.__private.models.disabled_api import DisabledAPI
from clive.__private.models.hp_vests_balance import HpVestsBalance

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.authority import Authority
    from clive.__private.core.commands.data_retrieval.update_node_data.models import NodeData


@dataclass
class CachedAuthorityRole:
    key_auths: list[tuple[str, int]]
    account_auths: list[tuple[str, int]]
    weight_threshold: int


@dataclass
class CachedAuthority:
    owner: CachedAuthorityRole
    active: CachedAuthorityRole
    posting: CachedAuthorityRole
    memo_key: str
    fetch_time: datetime


@dataclass
class CachedTapos:
    ref_block_num: int
    ref_block_prefix: int
    head_block_time: datetime


@dataclass
class CachedNodeData:
    """Cached subset of NodeData for offline display."""

    hive_balance_amount: int
    hbd_balance_amount: int
    hive_savings_amount: int
    hbd_savings_amount: int
    hive_unclaimed_amount: int
    hbd_unclaimed_amount: int
    owned_vests_amount: int
    owned_hp_amount: int
    unclaimed_vests_amount: int
    unclaimed_hp_amount: int
    vote_manabar_value: int
    vote_manabar_max: int
    vote_manabar_regen_secs: int
    downvote_manabar_value: int
    downvote_manabar_max: int
    downvote_manabar_regen_secs: int
    rc_manabar_value: int | None
    rc_manabar_max: int | None
    rc_manabar_regen_secs: int | None
    proxy: str
    recovery_account: str
    pending_claimed_accounts: int
    governance_vote_expiration_ts: datetime | None
    has_voting_rights: bool
    last_refresh: datetime | None
    last_history_entry: datetime | None
    last_account_update: datetime | None
    fetch_time: datetime

    @staticmethod
    def from_node_data(data: NodeData, fetch_time: datetime) -> CachedNodeData:
        """Extract cacheable fields from NodeData."""
        rc = data.rc_manabar
        if isinstance(rc, DisabledAPI):
            rc_value, rc_max, rc_regen = None, None, None
        else:
            rc_value = rc.value.amount
            rc_max = rc.max_value.amount
            rc_regen = int(rc.full_regeneration.total_seconds())

        return CachedNodeData(
            hive_balance_amount=data.hive_balance.amount,
            hbd_balance_amount=data.hbd_balance.amount,
            hive_savings_amount=data.hive_savings.amount,
            hbd_savings_amount=data.hbd_savings.amount,
            hive_unclaimed_amount=data.hive_unclaimed.amount,
            hbd_unclaimed_amount=data.hbd_unclaimed.amount,
            owned_vests_amount=data.owned_hp_balance.vests_balance.amount,
            owned_hp_amount=data.owned_hp_balance.hp_balance.amount,
            unclaimed_vests_amount=data.unclaimed_hp_balance.vests_balance.amount,
            unclaimed_hp_amount=data.unclaimed_hp_balance.hp_balance.amount,
            vote_manabar_value=data.vote_manabar.value.amount,
            vote_manabar_max=data.vote_manabar.max_value.amount,
            vote_manabar_regen_secs=int(data.vote_manabar.full_regeneration.total_seconds()),
            downvote_manabar_value=data.downvote_manabar.value.amount,
            downvote_manabar_max=data.downvote_manabar.max_value.amount,
            downvote_manabar_regen_secs=int(data.downvote_manabar.full_regeneration.total_seconds()),
            rc_manabar_value=rc_value,
            rc_manabar_max=rc_max,
            rc_manabar_regen_secs=rc_regen,
            proxy=data.proxy,
            recovery_account=data.recovery_account,
            pending_claimed_accounts=data.pending_claimed_accounts,
            governance_vote_expiration_ts=data.governance_vote_expiration_ts,
            has_voting_rights=data.has_voting_rights,
            last_refresh=data.last_refresh,
            last_history_entry=data.last_history_entry,
            last_account_update=data.last_account_update,
            fetch_time=fetch_time,
        )

    def to_node_data(self, authority: Authority) -> NodeData:
        """Reconstruct NodeData from cached fields + authority."""
        from clive.__private.core.commands.data_retrieval.update_node_data.models import (  # noqa: PLC0415
            Manabar as ManabarModel,
        )
        from clive.__private.core.commands.data_retrieval.update_node_data.models import (  # noqa: PLC0415
            NodeData as NodeDataModel,
        )

        def _build_manabar(value: int, max_value: int, regen_secs: int) -> ManabarModel:
            return ManabarModel(
                value=Asset.Hive(amount=value),
                max_value=Asset.Hive(amount=max_value),
                full_regeneration=timedelta(seconds=regen_secs),
            )

        rc_manabar: ManabarModel | DisabledAPI
        if (
            self.rc_manabar_value is not None
            and self.rc_manabar_max is not None
            and self.rc_manabar_regen_secs is not None
        ):
            rc_manabar = _build_manabar(self.rc_manabar_value, self.rc_manabar_max, self.rc_manabar_regen_secs)
        else:
            rc_manabar = DisabledAPI(missing_api="rc_api")

        return NodeDataModel(
            authority=authority,
            hive_balance=Asset.Hive(amount=self.hive_balance_amount),
            hbd_balance=Asset.Hbd(amount=self.hbd_balance_amount),
            hive_savings=Asset.Hive(amount=self.hive_savings_amount),
            hbd_savings=Asset.Hbd(amount=self.hbd_savings_amount),
            hive_unclaimed=Asset.Hive(amount=self.hive_unclaimed_amount),
            hbd_unclaimed=Asset.Hbd(amount=self.hbd_unclaimed_amount),
            owned_hp_balance=HpVestsBalance(
                hp_balance=Asset.Hive(amount=self.owned_hp_amount),
                vests_balance=Asset.Vests(amount=self.owned_vests_amount),
            ),
            unclaimed_hp_balance=HpVestsBalance(
                hp_balance=Asset.Hive(amount=self.unclaimed_hp_amount),
                vests_balance=Asset.Vests(amount=self.unclaimed_vests_amount),
            ),
            proxy=self.proxy,
            recovery_account=self.recovery_account,
            pending_claimed_accounts=self.pending_claimed_accounts,
            governance_vote_expiration_ts=self.governance_vote_expiration_ts or self.fetch_time,
            has_voting_rights=self.has_voting_rights,
            last_refresh=self.last_refresh or self.fetch_time,
            last_history_entry=self.last_history_entry or self.fetch_time,
            last_account_update=self.last_account_update or self.fetch_time,
            vote_manabar=_build_manabar(self.vote_manabar_value, self.vote_manabar_max, self.vote_manabar_regen_secs),
            downvote_manabar=_build_manabar(
                self.downvote_manabar_value, self.downvote_manabar_max, self.downvote_manabar_regen_secs
            ),
            rc_manabar=rc_manabar,
        )
