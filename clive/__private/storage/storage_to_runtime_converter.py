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
from clive.__private.models import Transaction
from clive.__private.storage import ProfileStorageModel
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers
    from clive.__private.core.profile import Profile


class AlarmIdentifierStorageToRuntimeConversionError(CliveError):
    """Exception raised when an alarm identifier cannot be converted to runtime."""


class StorageToRuntimeConverter:
    def __init__(self, model: ProfileStorageModel) -> None:
        self._model = model

    def create_profile(self) -> Profile:
        from clive.__private.core.profile import Profile

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

    def _working_account_from_model(self, model: ProfileStorageModel._TrackedAccountStorageModel) -> WorkingAccount:
        return WorkingAccount(model.name, self._alarms_storage_from_model(model))

    def _watched_account_from_model(self, model: ProfileStorageModel._TrackedAccountStorageModel) -> WatchedAccount:
        return WatchedAccount(model.name, self._alarms_storage_from_model(model))

    def _alarms_storage_from_model(self, model: ProfileStorageModel._TrackedAccountStorageModel) -> AlarmsStorage:
        alarms = [self._alarm_from_model(alarm) for alarm in model.alarms]
        return AlarmsStorage(alarms)

    def _known_account_from_model_representation(self, name: str) -> KnownAccount:
        return KnownAccount(name)

    def _alarm_from_model(self, model: ProfileStorageModel._AllAlarmStorageModel) -> AnyAlarm:
        alarm_cls = Alarm.get_alarm_class_by_name(model.name())
        identifier = self._alarm_identifier_from_model(model.identifier)
        return alarm_cls(identifier=identifier, is_harmless=model.is_harmless)

    def _alarm_identifier_from_model(
        self,
        model: ProfileStorageModel._DateTimeAlarmIdentifierStorageModel
        | ProfileStorageModel._RecoveryAccountWarningListedAlarmIdentifierStorageModel,
    ) -> AllAlarmIdentifiers:
        if isinstance(model, ProfileStorageModel._DateTimeAlarmIdentifierStorageModel):
            return DateTimeAlarmIdentifier(value=model.value)
        if isinstance(model, ProfileStorageModel._RecoveryAccountWarningListedAlarmIdentifierStorageModel):
            return RecoveryAccountWarningListedAlarmIdentifier(recovery_account=model.recovery_account)
        raise AlarmIdentifierStorageToRuntimeConversionError(
            f"Unknown alarm identifier storage model type: {type(model)}"
        )

    def _key_alias_from_model(self, model: ProfileStorageModel._KeyAliasStorageModel) -> PublicKeyAliased:
        return PublicKeyAliased(value=model.public_key, alias=model.alias)
