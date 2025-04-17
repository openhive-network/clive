from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from clive.__private.core.alarms.alarm_identifier import DateTimeAlarmIdentifier
from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)
from clive.__private.models.schemas import Transaction
from clive.__private.storage.model import ProfileStorageModel
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile import Profile


class AlarmIdentifierRuntimeToStorageConversionError(CliveError):
    """Exception raised when an alarm identifier cannot be converted to storage."""


class RuntimeToStorageConverter:
    def __init__(self, profile: Profile) -> None:
        self._profile = profile

    def create_storage_model(self) -> ProfileStorageModel:
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
        return ProfileStorageModel.TrackedAccountStorageModel(name=account.name, alarms=alarms)

    def _alarm_to_model(self, alarm: AnyAlarm) -> ProfileStorageModel.AlarmStorageModel:
        return ProfileStorageModel.AlarmStorageModel(
            name=alarm.get_name(),
            is_harmless=alarm.is_harmless,
            identifier=self._alarm_identifier_to_model(alarm.identifier_ensure),
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
