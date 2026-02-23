from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Final

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.__private.core.iwax import (
    calculate_current_manabar_value,
    calculate_manabar_full_regeneration_time,
)

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models.schemas import (
        DynamicGlobalProperties,
        FindRcAccounts,
        ListRcDirectDelegations,
        RcAccount,
        RcDirectDelegation,
    )

_MAX_RC_DIRECT_DELEGATIONS_LIMIT: Final[int] = 1000


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    rc_accounts: FindRcAccounts | None = None
    rc_delegations: ListRcDirectDelegations | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    rc_account: RcAccount
    outgoing_delegations: list[RcDirectDelegation]


@dataclass
class RcData:
    max_rc: int
    current_mana: int
    rc_percentage: Decimal
    delegated_rc: int
    received_delegated_rc: int
    effective_rc: int
    outgoing_delegations: list[RcDirectDelegation]
    full_regeneration: timedelta
    owned_rc_from_stake: int


@dataclass(kw_only=True)
class RcDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, RcData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.rc_api.find_rc_accounts(accounts=[self.account_name]),
                await node.api.rc_api.list_rc_direct_delegations(
                    start=(self.account_name, ""), limit=_MAX_RC_DIRECT_DELEGATIONS_LIMIT
                ),
            )
        raise bke.UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self._assert_gdpo(data.gdpo),
            rc_account=self._assert_rc_account(data.rc_accounts),
            outgoing_delegations=self._assert_delegations(data.rc_delegations),
        )

    async def _process_data(self, data: SanitizedData) -> RcData:
        rc_account = data.rc_account
        max_rc = int(rc_account.max_rc)
        delegated_rc = int(rc_account.delegated_rc)
        received_delegated_rc = int(rc_account.received_delegated_rc)
        owned_rc_from_stake = max_rc + delegated_rc - received_delegated_rc

        head_block_time = data.gdpo.time
        head_block_timestamp = int(head_block_time.timestamp())
        last_update_timestamp = rc_account.rc_manabar.last_update_time
        current_mana_raw = rc_account.rc_manabar.current_mana

        current_mana = calculate_current_manabar_value(
            now=head_block_timestamp,
            max_mana=max_rc,
            current_mana=current_mana_raw,
            last_update_time=last_update_timestamp,
        )

        precision = HIVE_PERCENT_PRECISION_DOT_PLACES
        if max_rc > 0:
            rc_percentage = DecimalConverter.round_to_precision(
                Decimal(current_mana) * 100 / Decimal(max_rc), precision=precision
            )
        else:
            rc_percentage = DecimalConverter.convert(0, precision=precision)

        if max_rc > 0:
            full_regeneration_dt = calculate_manabar_full_regeneration_time(
                now=head_block_timestamp,
                max_mana=max_rc,
                current_mana=current_mana_raw,
                last_update_time=last_update_timestamp,
            )
            full_regeneration = full_regeneration_dt - head_block_time
        else:
            full_regeneration = timedelta(0)

        # Filter delegations to only include those from this account
        outgoing_delegations = [d for d in data.outgoing_delegations if str(d.from_) == self.account_name]

        return RcData(
            max_rc=max_rc,
            current_mana=current_mana,
            rc_percentage=rc_percentage,
            delegated_rc=delegated_rc,
            received_delegated_rc=received_delegated_rc,
            effective_rc=max_rc,
            outgoing_delegations=outgoing_delegations,
            full_regeneration=full_regeneration,
            owned_rc_from_stake=owned_rc_from_stake,
        )

    def _assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def _assert_rc_account(self, data: FindRcAccounts | None) -> RcAccount:
        assert data is not None, "FindRcAccounts data is missing"
        assert len(data.rc_accounts) == 1, "Invalid amount of RC accounts"

        rc_account = data.rc_accounts[0]
        assert str(rc_account.account) == self.account_name, "Invalid RC account name"
        return rc_account

    def _assert_delegations(self, data: ListRcDirectDelegations | None) -> list[RcDirectDelegation]:
        assert data is not None, "ListRcDirectDelegations data is missing"
        return data.rc_direct_delegations
