from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.date_utils import utc_epoch
from wax._private.models.hive_date_time import HiveDateTime
from wax.interfaces import IAuthorityDataProvider
from wax.models.authority import WaxAccountAuthorityInfo, WaxAuthorities, WaxAuthority

if TYPE_CHECKING:
    from clive.__private.core.cached_offline_data import CachedAuthority, CachedAuthorityRole
    from wax.models.basic import AccountName


class CachedAuthorityDataProvider(IAuthorityDataProvider):
    """Provides authority data from cached offline data for reconstructing Authority objects."""

    def __init__(self, cached_authority: CachedAuthority, account_name: str) -> None:
        self._cached = cached_authority
        self._account_name = account_name

    async def get_hive_authority_data(self, name: AccountName) -> WaxAccountAuthorityInfo:
        assert name == self._account_name, f"Account name mismatch: got `{self._account_name}` expected `{name}`."

        def role_to_wax(role: CachedAuthorityRole) -> WaxAuthority:
            return WaxAuthority(
                weight_threshold=role.weight_threshold,
                account_auths=dict(role.account_auths),
                key_auths=dict(role.key_auths),
            )

        authorities = WaxAuthorities(
            owner=role_to_wax(self._cached.owner),
            active=role_to_wax(self._cached.active),
            posting=role_to_wax(self._cached.posting),
        )

        epoch = HiveDateTime(utc_epoch())
        return WaxAccountAuthorityInfo(
            account=self._account_name,
            authorities=authorities,
            memo_key=self._cached.memo_key,
            last_owner_update=epoch,
            previous_owner_update=epoch,
        )
