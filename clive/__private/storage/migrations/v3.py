from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from typing import Self

from clive.__private.models.schemas import HiveDateTime, PreconfiguredBaseModel
from clive.__private.storage.migrations import v2


class ProfileStorageModel(v2.ProfileStorageModel):
    cached_ref_block_num: int | None = None
    cached_ref_block_prefix: int | None = None
    cached_head_block_time: HiveDateTime | None = None

    class AuthorityRoleCacheStorageModel(PreconfiguredBaseModel):
        key_auths: list[list[str | int]] | None = None
        account_auths: list[list[str | int]] | None = None
        weight_threshold: int | None = None

    class AuthorityCacheStorageModel(PreconfiguredBaseModel):
        owner: ProfileStorageModel.AuthorityRoleCacheStorageModel | None = None
        active: ProfileStorageModel.AuthorityRoleCacheStorageModel | None = None
        posting: ProfileStorageModel.AuthorityRoleCacheStorageModel | None = None
        memo_key: str | None = None
        fetch_time: HiveDateTime | None = None

    class NodeDataCacheStorageModel(PreconfiguredBaseModel):
        hive_balance_amount: int = 0
        hbd_balance_amount: int = 0
        hive_savings_amount: int = 0
        hbd_savings_amount: int = 0
        hive_unclaimed_amount: int = 0
        hbd_unclaimed_amount: int = 0
        owned_vests_amount: int = 0
        owned_hp_amount: int = 0
        unclaimed_vests_amount: int = 0
        unclaimed_hp_amount: int = 0
        vote_manabar_value: int = 0
        vote_manabar_max: int = 0
        vote_manabar_regen_secs: int = 0
        downvote_manabar_value: int = 0
        downvote_manabar_max: int = 0
        downvote_manabar_regen_secs: int = 0
        rc_manabar_value: int | None = None
        rc_manabar_max: int | None = None
        rc_manabar_regen_secs: int | None = None
        proxy: str = ""
        recovery_account: str = ""
        pending_claimed_accounts: int = 0
        governance_vote_expiration_ts: HiveDateTime | None = None
        has_voting_rights: bool = True
        last_refresh: HiveDateTime | None = None
        last_history_entry: HiveDateTime | None = None
        last_account_update: HiveDateTime | None = None
        fetch_time: HiveDateTime | None = None

    class TrackedAccountStorageModel(v2.ProfileStorageModel.TrackedAccountStorageModel):
        authority_cache: ProfileStorageModel.AuthorityCacheStorageModel | None = None
        node_data_cache: ProfileStorageModel.NodeDataCacheStorageModel | None = None

    tracked_accounts: Sequence[TrackedAccountStorageModel] = []

    @classmethod
    def upgrade(cls, old: v2.ProfileStorageModel) -> Self:  # type: ignore[override]  # should always take previous model
        old_dict = old.dict()

        # Convert tracked accounts to new model with authority_cache=None
        old_tracked_models = old.tracked_accounts
        old_dict.pop("tracked_accounts", None)
        new_tracked = [cls.TrackedAccountStorageModel(**ta.dict()) for ta in old_tracked_models]

        return cls(
            **old_dict,
            tracked_accounts=new_tracked,
        )
