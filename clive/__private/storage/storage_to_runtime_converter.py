from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.accounts.accounts import KnownAccount, WatchedAccount, WorkingAccount
from clive.__private.core.alarms.alarm import Alarm
from clive.__private.core.alarms.alarms_storage import AlarmsStorage
from clive.__private.core.authority import AllAuthorities, Authority
from clive.__private.core.keys import PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import OperationBase
    from clive.__private.storage.model import (
        AlarmStorageModel,
        AllAuthoritiesStorageModel,
        AuthorityStorageModel,
        KeyAliasStorageModel,
        ProfileStorageModel,
        TrackedAccountStorageModel,
    )


class StorageToRuntimeConverter:
    def __init__(self, model: ProfileStorageModel) -> None:
        self._model = model

    def create_profile(self) -> Profile:
        from clive.__private.core.profile import Profile

        return Profile.create(
            name=self._model.name,
            working_account=self._working_account_from_profile_storage_model(),
            watched_accounts=self._watched_accounts_from_profile_storage_model(),
            known_accounts=self._known_accounts_from_profile_storage_model(),
            key_aliases=self._key_aliases_from_profile_storage_model(),
            cart_operations=self._operations_from_model(),
            chain_id=self._model.chain_id,
            node_address=self._model.node_address,
            is_newly_created=False,
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

    def _operations_from_model(self) -> list[OperationBase]:
        return [op_repr.value for op_repr in self._model.cart_operations]  # type: ignore[attr-defined]

    def _working_account_from_model(self, model: TrackedAccountStorageModel) -> WorkingAccount:
        return WorkingAccount(
            model.name, self._alarms_storage_from_model(model), self._all_authorities_from_model(model.authorities)
        )

    def _watched_account_from_model(self, model: TrackedAccountStorageModel) -> WatchedAccount:
        return WatchedAccount(
            model.name, self._alarms_storage_from_model(model), self._all_authorities_from_model(model.authorities)
        )

    def _alarms_storage_from_model(self, model: TrackedAccountStorageModel) -> AlarmsStorage:
        alarms = [self._alarm_from_model(alarm) for alarm in model.alarms]
        return AlarmsStorage(alarms)

    def _known_account_from_model_representation(self, name: str) -> KnownAccount:
        return KnownAccount(name)

    def _alarm_from_model(self, model: AlarmStorageModel) -> AnyAlarm:
        alarm_cls = Alarm.get_alarm_class_by_name(model.name)
        return alarm_cls(identifier=model.identifier, is_harmless=model.is_harmless)

    def _key_alias_from_model(self, model: KeyAliasStorageModel) -> PublicKeyAliased:
        return PublicKeyAliased(value=model.public_key, alias=model.alias)

    def _all_authorities_from_model(
        self, authorities_model: AllAuthoritiesStorageModel | None
    ) -> AllAuthorities | None:
        if authorities_model is None:
            return None
        return AllAuthorities(
            owner=self._authority_from_model(authorities_model.owner),
            active=self._authority_from_model(authorities_model.active),
            posting=self._authority_from_model(authorities_model.posting),
            owner_lut=self._authority_lut_from_model(authorities_model.owner_lut),
            active_lut=self._authority_lut_from_model(authorities_model.active_lut),
            posting_lut=self._authority_lut_from_model(authorities_model.posting_lut),
            last_updated=authorities_model.last_updated,
        )

    def _authority_lut_from_model(self, lut_model: dict[str, AuthorityStorageModel]) -> dict[str, Authority]:
        lut: dict[str, Authority] = {}
        for name, authority_model in lut_model.items():
            lut[name] = self._authority_from_model(authority_model)
        return lut

    def _authority_from_model(self, authority_model: AuthorityStorageModel) -> Authority:
        return Authority(
            weight_threshold=authority_model.weight_threshold,
            account_auths=authority_model.account_auths.copy(),
            key_auths=authority_model.key_auths.copy(),
        )
