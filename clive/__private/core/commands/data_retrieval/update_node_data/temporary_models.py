from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.date_utils import utc_epoch

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.authority import Authority
    from clive.__private.models.schemas import (
        Account,
        DynamicGlobalProperties,
        FindAccounts,
        FindRcAccounts,
        GetAccountHistory,
        RcAccount,
    )


@dataclass
class AccountHarvestedDataRaw:
    core: Account | None = None
    rc: RcAccount | None = None
    account_history: GetAccountHistory | None = None


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    core_accounts: FindAccounts | None = None
    rc_accounts: FindRcAccounts | None = None
    account_harvested_data: dict[TrackedAccount, AccountHarvestedDataRaw] = field(
        default_factory=lambda: defaultdict(AccountHarvestedDataRaw)
    )


@dataclass
class AccountSanitizedData:
    core: Account
    account_history: GetAccountHistory | None = None
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""


AccountSanitizedDataContainer = dict[TrackedAccount, AccountSanitizedData]


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    account_sanitized_data: AccountSanitizedDataContainer


@dataclass
class AccountProcessedData:
    core: Account
    authority: Authority
    last_history_entry: datetime = field(default_factory=lambda: utc_epoch())
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""
