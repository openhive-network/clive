from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import convert_to_representation
from clive.__private.storage.model import (
    AlarmStorageModel,
    AuthoritiesStorageModel,
    AuthorityStorageModel,
    KeyAliasStorageModel,
    ProfileStorageModel,
    TrackedAccountStorageModel,
)

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.types import AuthoritiesT
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import OperationRepresentationBase


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
            cart_operations=self._operations_to_model_container(),
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

    def _operations_to_model_container(self) -> list[OperationRepresentationBase]:
        return [convert_to_representation(operation) for operation in self._profile.cart]

    def _tracked_account_to_model(self, account: TrackedAccount) -> TrackedAccountStorageModel:
        alarms = [self._alarm_to_model(alarm) for alarm in account._alarms.all_alarms if alarm.has_identifier]
        return TrackedAccountStorageModel(
            name=account.name, alarms=alarms, authorities=self._all_authorities_to_model(account._authorities)
        )

    def _alarm_to_model(self, alarm: AnyAlarm) -> AlarmStorageModel:
        return AlarmStorageModel(
            name=alarm.get_name(), is_harmless=alarm.is_harmless, identifier=alarm.identifier_ensure
        )

    def _key_alias_to_model(self, key: PublicKeyAliased) -> KeyAliasStorageModel:
        return KeyAliasStorageModel(alias=key.alias, public_key=key.value)

    def _all_authorities_to_model(self, authorities: AllAuthorities | None) -> AllAuthoritiesStorageModel | None:
        if authorities is None:
            return None
        return AllAuthoritiesStorageModel(
            owner=self._authority_to_model(authorities.owner),
            active=self._authority_to_model(authorities.active),
            posting=self._authority_to_model(authorities.posting),
            owner_lut=self._authority_lut_to_model(authorities.owner_lut),
            active_lut=self._authority_lut_to_model(authorities.owner_lut),
            posting_lut=self._authority_lut_to_model(authorities.owner_lut),
            last_updated=authorities.last_updated,
        )

    def _authority_lut_to_model(self, lut: dict[str, Authority]) -> dict[str, AuthorityStorageModel]:
        lut_model: dict[str, AuthorityStorageModel] = {}
        for name, authority in lut.items():
            lut_model[name] = self._authority_to_model(authority)
        return lut_model

    def _authority_to_model(self, authority: Authority) -> AuthorityStorageModel:
        return AuthorityStorageModel(
            weight_threshold=authority.weight_threshold,
            account_auths=authority.account_auths.copy(),
            key_auths=authority.key_auths.copy(),
        )
