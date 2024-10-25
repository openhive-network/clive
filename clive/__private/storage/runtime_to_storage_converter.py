from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from clive.__private.storage.model import (
    AlarmStorageModel,
    KeyAliasStorageModel,
    ProfileStorageModel,
    TrackedAccountStorageModel,
    TransactionCoreStorageModel,
    TransactionStorageModel,
)

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile import Profile


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
        )

    def _working_account_to_model_representation(self) -> str | None:
        profile = self._profile
        return profile.accounts.working.name if profile.accounts.has_working_account else None

    def _tracked_accounts_to_model_container(self) -> list[TrackedAccountStorageModel]:
        return [self._tracked_account_to_model(account) for account in self._profile.accounts.tracked]

    def _known_accounts_to_model_container(self) -> list[str]:
        return [account.name for account in self._profile.accounts.known]

    def _key_aliases_to_model_container(self) -> list[KeyAliasStorageModel]:
        return [self._key_alias_to_model(key) for key in self._profile.keys]

    def _transaction_to_model(self) -> TransactionStorageModel:
        transaction_core = TransactionCoreStorageModel(
            operations=deepcopy(self._profile.operation_representations),
            ref_block_num=self._profile.transaction.ref_block_num,
            ref_block_prefix=self._profile.transaction.ref_block_prefix,
            expiration=self._profile.transaction.expiration,
            extensions=deepcopy(self._profile.transaction.extensions),
            signatures=deepcopy(self._profile.transaction.signatures),
        )
        return TransactionStorageModel(
            transaction_core=transaction_core, transaction_file_path=self._profile.transaction_file_path
        )

    def _tracked_account_to_model(self, account: TrackedAccount) -> TrackedAccountStorageModel:
        alarms = [self._alarm_to_model(alarm) for alarm in account._alarms.all_alarms if alarm.has_identifier]
        return TrackedAccountStorageModel(name=account.name, alarms=alarms)

    def _alarm_to_model(self, alarm: AnyAlarm) -> AlarmStorageModel:
        return AlarmStorageModel(
            name=alarm.get_name(), is_harmless=alarm.is_harmless, identifier=alarm.identifier_ensure
        )

    def _key_alias_to_model(self, key: PublicKeyAliased) -> KeyAliasStorageModel:
        return KeyAliasStorageModel(alias=key.alias, public_key=key.value)
