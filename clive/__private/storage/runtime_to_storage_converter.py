from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, get_args

from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)
from clive.__private.models.schemas import HiveDateTime, Transaction
from clive.__private.storage.current_model import ProfileStorageModel
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier
    from clive.__private.core.cached_offline_data import CachedAuthority, CachedAuthorityRole, CachedNodeData
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile import Profile


class AlarmIdentifierRuntimeToStorageConversionError(CliveError):
    """Exception raised when an alarm identifier cannot be converted to storage."""


class RuntimeToStorageConverter:
    def __init__(self, profile: Profile) -> None:
        self._profile = profile

    def create_storage_model(self) -> ProfileStorageModel:
        cached_tapos = self._profile.cached_tapos
        return ProfileStorageModel(
            name=self._profile.name,
            working_account=self._working_account_to_model_representation(),
            tracked_accounts=self._tracked_accounts_to_model_container(),
            known_accounts=self._known_accounts_to_model_container(),
            key_aliases=self._key_aliases_to_model_container(),
            transaction=self._transaction_to_model(),
            chain_id=self._profile.chain_id,
            node_address=str(self._profile.node_address),
            tui_theme=self._profile.tui_theme,
            should_enable_known_accounts=self._profile.should_enable_known_accounts,
            cached_ref_block_num=cached_tapos.ref_block_num if cached_tapos else None,
            cached_ref_block_prefix=cached_tapos.ref_block_prefix if cached_tapos else None,
            cached_head_block_time=HiveDateTime(cached_tapos.head_block_time) if cached_tapos else None,
        )

    def _working_account_to_model_representation(self) -> str | None:
        profile = self._profile
        return profile.accounts.working.name if profile.accounts.has_working_account else None

    def _tracked_accounts_to_model_container(self) -> list[ProfileStorageModel.TrackedAccountStorageModel]:
        return [self._tracked_account_to_model(account) for account in self._profile.accounts.tracked]

    def _known_accounts_to_model_container(self) -> list[str]:
        return [account.name for account in self._profile.accounts.known]

    def _key_aliases_to_model_container(self) -> list[ProfileStorageModel.KeyAliasStorageModel]:
        return [self._key_alias_to_model(key) for key in self._profile.keys]

    def _transaction_to_model(self) -> ProfileStorageModel.TransactionStorageModel:
        transaction_core = Transaction(
            operations=deepcopy(self._profile.operation_representations),
            ref_block_num=self._profile.transaction.ref_block_num,
            ref_block_prefix=self._profile.transaction.ref_block_prefix,
            expiration=self._profile.transaction.expiration,
            extensions=deepcopy(self._profile.transaction.extensions),
            signatures=deepcopy(self._profile.transaction.signatures),
        )
        return ProfileStorageModel.TransactionStorageModel(
            transaction_core=transaction_core, transaction_file_path=self._profile.transaction_file_path
        )

    def _tracked_account_to_model(self, account: TrackedAccount) -> ProfileStorageModel.TrackedAccountStorageModel:
        alarms = [self._alarm_to_model(alarm) for alarm in account._alarms.all_alarms if alarm.has_identifier]
        return ProfileStorageModel.TrackedAccountStorageModel(
            name=account.name,
            alarms=alarms,
            authority_cache=self._authority_cache_to_model(account._cached_authority),
            node_data_cache=self._node_data_cache_to_model(account._cached_node_data),
        )

    def _alarm_to_model(self, alarm: AnyAlarm) -> ProfileStorageModel.AllAlarmStorageModel:
        alarm_cls = self._get_alarm_storage_model_cls_by_name(alarm.get_name())
        return alarm_cls(
            is_harmless=alarm.is_harmless,
            identifier=self._alarm_identifier_to_model(alarm.identifier_ensure),  # type: ignore[arg-type]
        )

    def _alarm_identifier_to_model(
        self, identifier: AlarmIdentifier
    ) -> ProfileStorageModel.AllAlarmIdentifiersStorageModel:
        if isinstance(identifier, DateTimeAlarmIdentifier):
            return ProfileStorageModel.DateTimeAlarmIdentifierStorageModel(value=identifier.value)
        if isinstance(identifier, RecoveryAccountWarningListedAlarmIdentifier):
            return ProfileStorageModel.RecoveryAccountWarningListedAlarmIdentifierStorageModel(
                recovery_account=identifier.recovery_account
            )
        raise AlarmIdentifierRuntimeToStorageConversionError(f"Unknown alarm identifier type: {type(identifier)}")

    def _key_alias_to_model(self, key: PublicKeyAliased) -> ProfileStorageModel.KeyAliasStorageModel:
        return ProfileStorageModel.KeyAliasStorageModel(alias=key.alias, public_key=key.value)

    def _get_alarm_storage_model_cls_by_name(self, name: str) -> type[ProfileStorageModel.AllAlarmStorageModel]:
        all_alarm_storage_model_classes = get_args(ProfileStorageModel.AllAlarmStorageModel)
        name_to_cls: dict[str, type[ProfileStorageModel.AllAlarmStorageModel]] = {
            cls.get_name(): cls for cls in all_alarm_storage_model_classes
        }
        assert name in name_to_cls, f"Alarm class not found for name: {name}"
        return name_to_cls[name]

    def _authority_cache_to_model(
        self, cached: CachedAuthority | None
    ) -> ProfileStorageModel.AuthorityCacheStorageModel | None:
        if cached is None:
            return None
        return ProfileStorageModel.AuthorityCacheStorageModel(
            owner=self._authority_role_to_model(cached.owner),
            active=self._authority_role_to_model(cached.active),
            posting=self._authority_role_to_model(cached.posting),
            memo_key=cached.memo_key,
            fetch_time=HiveDateTime(cached.fetch_time),
        )

    def _authority_role_to_model(self, role: CachedAuthorityRole) -> ProfileStorageModel.AuthorityRoleCacheStorageModel:
        return ProfileStorageModel.AuthorityRoleCacheStorageModel(
            key_auths=[[k, w] for k, w in role.key_auths],
            account_auths=[[a, w] for a, w in role.account_auths],
            weight_threshold=role.weight_threshold,
        )

    def _node_data_cache_to_model(
        self, cached: CachedNodeData | None
    ) -> ProfileStorageModel.NodeDataCacheStorageModel | None:
        if cached is None:
            return None
        return ProfileStorageModel.NodeDataCacheStorageModel(
            hive_balance_amount=cached.hive_balance_amount,
            hbd_balance_amount=cached.hbd_balance_amount,
            hive_savings_amount=cached.hive_savings_amount,
            hbd_savings_amount=cached.hbd_savings_amount,
            hive_unclaimed_amount=cached.hive_unclaimed_amount,
            hbd_unclaimed_amount=cached.hbd_unclaimed_amount,
            owned_vests_amount=cached.owned_vests_amount,
            owned_hp_amount=cached.owned_hp_amount,
            unclaimed_vests_amount=cached.unclaimed_vests_amount,
            unclaimed_hp_amount=cached.unclaimed_hp_amount,
            vote_manabar_value=cached.vote_manabar_value,
            vote_manabar_max=cached.vote_manabar_max,
            vote_manabar_regen_secs=cached.vote_manabar_regen_secs,
            downvote_manabar_value=cached.downvote_manabar_value,
            downvote_manabar_max=cached.downvote_manabar_max,
            downvote_manabar_regen_secs=cached.downvote_manabar_regen_secs,
            rc_manabar_value=cached.rc_manabar_value,
            rc_manabar_max=cached.rc_manabar_max,
            rc_manabar_regen_secs=cached.rc_manabar_regen_secs,
            proxy=cached.proxy,
            recovery_account=cached.recovery_account,
            pending_claimed_accounts=cached.pending_claimed_accounts,
            governance_vote_expiration_ts=(
                HiveDateTime(cached.governance_vote_expiration_ts) if cached.governance_vote_expiration_ts else None
            ),
            has_voting_rights=cached.has_voting_rights,
            last_refresh=HiveDateTime(cached.last_refresh) if cached.last_refresh else None,
            last_history_entry=HiveDateTime(cached.last_history_entry) if cached.last_history_entry else None,
            last_account_update=HiveDateTime(cached.last_account_update) if cached.last_account_update else None,
            fetch_time=HiveDateTime(cached.fetch_time) if cached.fetch_time else None,
        )
