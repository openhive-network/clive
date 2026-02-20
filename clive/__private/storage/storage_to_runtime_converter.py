from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from clive.__private.core.accounts.accounts import KnownAccount, WatchedAccount, WorkingAccount
from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.alarms.alarms_storage import AlarmsStorage
from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)
from clive.__private.core.keys import PublicKeyAliased
from clive.__private.models.transaction import Transaction
from clive.__private.storage.current_model import ProfileStorageModel
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers
    from clive.__private.core.cached_offline_data import (
        CachedAuthority,
        CachedAuthorityRole,
        CachedNodeData,
        CachedTapos,
    )
    from clive.__private.core.profile import Profile


class AlarmIdentifierStorageToRuntimeConversionError(CliveError):
    """Exception raised when an alarm identifier cannot be converted to runtime."""


class StorageToRuntimeConverter:
    def __init__(self, model: ProfileStorageModel) -> None:
        self._model = model

    def create_profile(self) -> Profile:
        from clive.__private.core.profile import Profile  # noqa: PLC0415

        return Profile._create_instance(
            name=self._model.name,
            working_account=self._working_account_from_profile_storage_model(),
            watched_accounts=self._watched_accounts_from_profile_storage_model(),
            known_accounts=self._known_accounts_from_profile_storage_model(),
            key_aliases=self._key_aliases_from_profile_storage_model(),
            transaction=self._transaction_core_from_storage_model(),
            transaction_file_path=self._transaction_file_path_from_storage_model(),
            chain_id=self._model.chain_id,
            node_address=self._model.node_address,
            tui_theme=self._model.tui_theme,
            should_enable_known_accounts=self._model.should_enable_known_accounts,
            cached_tapos=self._cached_tapos_from_model(),
        )

    def _working_account_from_profile_storage_model(self) -> WorkingAccount | None:
        working_account_name = self._model.working_account
        is_working_account_set = working_account_name is not None
        if not is_working_account_set:
            return None

        working_account_model = next(
            (account for account in self._model.tracked_accounts if account.name == working_account_name), None
        )
        message = f"Working account: {working_account_name} not found in tracked accounts in the profile storage model."
        assert working_account_model is not None, message
        return self._working_account_from_model(working_account_model)

    def _watched_accounts_from_profile_storage_model(self) -> set[WatchedAccount]:
        working_account_name = self._model.working_account
        return {
            self._watched_account_from_model(account)
            for account in self._model.tracked_accounts
            if account.name != working_account_name
        }

    def _known_accounts_from_profile_storage_model(self) -> set[KnownAccount]:
        return {self._known_account_from_model_representation(account) for account in self._model.known_accounts}

    def _key_aliases_from_profile_storage_model(self) -> set[PublicKeyAliased]:
        return {self._key_alias_from_model(key) for key in self._model.key_aliases}

    def _transaction_core_from_storage_model(self) -> Transaction | None:
        transaction_storage_model = self._model.transaction

        if transaction_storage_model is None:
            return None

        transaction_core = transaction_storage_model.transaction_core
        return Transaction(
            operations=deepcopy(transaction_core.operations),
            ref_block_num=transaction_core.ref_block_num,
            ref_block_prefix=transaction_core.ref_block_prefix,
            expiration=transaction_core.expiration,
            extensions=deepcopy(transaction_core.extensions),
            signatures=deepcopy(transaction_core.signatures),
        )

    def _transaction_file_path_from_storage_model(self) -> Path | None:
        transaction_storage_model = self._model.transaction

        if transaction_storage_model:
            return transaction_storage_model.transaction_file_path
        return None

    def _working_account_from_model(self, model: ProfileStorageModel.TrackedAccountStorageModel) -> WorkingAccount:
        authority_cache = self._authority_cache_from_model(getattr(model, "authority_cache", None))
        node_data_cache = self._node_data_cache_from_model(getattr(model, "node_data_cache", None))
        return WorkingAccount(
            model.name,
            self._alarms_storage_from_model(model),
            _cached_authority=authority_cache,
            _cached_node_data=node_data_cache,
        )

    def _watched_account_from_model(self, model: ProfileStorageModel.TrackedAccountStorageModel) -> WatchedAccount:
        authority_cache = self._authority_cache_from_model(getattr(model, "authority_cache", None))
        node_data_cache = self._node_data_cache_from_model(getattr(model, "node_data_cache", None))
        return WatchedAccount(
            model.name,
            self._alarms_storage_from_model(model),
            _cached_authority=authority_cache,
            _cached_node_data=node_data_cache,
        )

    def _alarms_storage_from_model(self, model: ProfileStorageModel.TrackedAccountStorageModel) -> AlarmsStorage:
        alarms = [self._alarm_from_model(alarm) for alarm in model.alarms]
        return AlarmsStorage(alarms)

    def _known_account_from_model_representation(self, name: str) -> KnownAccount:
        return KnownAccount(name)

    def _alarm_from_model(self, model: ProfileStorageModel.AllAlarmStorageModel) -> AnyAlarm:
        alarm_cls = Alarm.get_alarm_class_by_name(model.get_name())
        identifier = self._alarm_identifier_from_model(model.identifier)
        return alarm_cls(identifier=identifier, is_harmless=model.is_harmless)

    def _alarm_identifier_from_model(
        self, model: ProfileStorageModel.AllAlarmIdentifiersStorageModel
    ) -> AllAlarmIdentifiers:
        if isinstance(model, ProfileStorageModel.DateTimeAlarmIdentifierStorageModel):
            return DateTimeAlarmIdentifier(value=model.value)
        if isinstance(model, ProfileStorageModel.RecoveryAccountWarningListedAlarmIdentifierStorageModel):
            return RecoveryAccountWarningListedAlarmIdentifier(recovery_account=model.recovery_account)
        raise AlarmIdentifierStorageToRuntimeConversionError(
            f"Unknown alarm identifier storage model type: {type(model)}"
        )

    def _key_alias_from_model(self, model: ProfileStorageModel.KeyAliasStorageModel) -> PublicKeyAliased:
        return PublicKeyAliased(value=model.public_key, alias=model.alias)

    def _cached_tapos_from_model(self) -> CachedTapos | None:
        ref_block_num = getattr(self._model, "cached_ref_block_num", None)
        ref_block_prefix = getattr(self._model, "cached_ref_block_prefix", None)
        head_block_time = getattr(self._model, "cached_head_block_time", None)

        if ref_block_num is None or ref_block_prefix is None or head_block_time is None:
            return None

        from clive.__private.core.cached_offline_data import CachedTapos as CachedTaposRuntime  # noqa: PLC0415

        return CachedTaposRuntime(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            head_block_time=head_block_time,
        )

    def _authority_cache_from_model(
        self, model: ProfileStorageModel.AuthorityCacheStorageModel | None
    ) -> CachedAuthority | None:
        if model is None:
            return None
        if model.owner is None or model.active is None or model.posting is None:
            return None
        if model.memo_key is None or model.fetch_time is None:
            return None

        from clive.__private.core.cached_offline_data import CachedAuthority as CachedAuthorityRuntime  # noqa: PLC0415

        return CachedAuthorityRuntime(
            owner=self._authority_role_from_model(model.owner),
            active=self._authority_role_from_model(model.active),
            posting=self._authority_role_from_model(model.posting),
            memo_key=model.memo_key,
            fetch_time=model.fetch_time,
        )

    def _authority_role_from_model(
        self, model: ProfileStorageModel.AuthorityRoleCacheStorageModel
    ) -> CachedAuthorityRole:
        from clive.__private.core.cached_offline_data import (  # noqa: PLC0415
            CachedAuthorityRole as CachedAuthorityRoleRuntime,
        )

        key_auths = [(str(pair[0]), int(pair[1])) for pair in (model.key_auths or [])]
        account_auths = [(str(pair[0]), int(pair[1])) for pair in (model.account_auths or [])]
        return CachedAuthorityRoleRuntime(
            key_auths=key_auths,
            account_auths=account_auths,
            weight_threshold=model.weight_threshold or 0,
        )

    def _node_data_cache_from_model(
        self, model: ProfileStorageModel.NodeDataCacheStorageModel | None
    ) -> CachedNodeData | None:
        if model is None:
            return None
        if model.fetch_time is None:
            return None

        from clive.__private.core.cached_offline_data import CachedNodeData as CachedNodeDataRuntime  # noqa: PLC0415

        return CachedNodeDataRuntime(
            hive_balance_amount=model.hive_balance_amount,
            hbd_balance_amount=model.hbd_balance_amount,
            hive_savings_amount=model.hive_savings_amount,
            hbd_savings_amount=model.hbd_savings_amount,
            hive_unclaimed_amount=model.hive_unclaimed_amount,
            hbd_unclaimed_amount=model.hbd_unclaimed_amount,
            owned_vests_amount=model.owned_vests_amount,
            owned_hp_amount=model.owned_hp_amount,
            unclaimed_vests_amount=model.unclaimed_vests_amount,
            unclaimed_hp_amount=model.unclaimed_hp_amount,
            vote_manabar_value=model.vote_manabar_value,
            vote_manabar_max=model.vote_manabar_max,
            vote_manabar_regen_secs=model.vote_manabar_regen_secs,
            downvote_manabar_value=model.downvote_manabar_value,
            downvote_manabar_max=model.downvote_manabar_max,
            downvote_manabar_regen_secs=model.downvote_manabar_regen_secs,
            rc_manabar_value=model.rc_manabar_value,
            rc_manabar_max=model.rc_manabar_max,
            rc_manabar_regen_secs=model.rc_manabar_regen_secs,
            proxy=model.proxy,
            recovery_account=model.recovery_account,
            pending_claimed_accounts=model.pending_claimed_accounts,
            governance_vote_expiration_ts=model.governance_vote_expiration_ts,
            has_voting_rights=model.has_voting_rights,
            last_refresh=model.last_refresh,
            last_history_entry=model.last_history_entry,
            last_account_update=model.last_account_update,
            fetch_time=model.fetch_time,
        )
