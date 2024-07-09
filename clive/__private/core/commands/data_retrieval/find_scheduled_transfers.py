from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final, Literal, Sequence, TypeVar, cast

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.constants.node import VALUE_TO_REMOVE_SCHEDULED_TRANSFER
from clive.__private.core.formatters.humanize import align_to_dot, humanize_asset

if TYPE_CHECKING:
    from clive.models.aliased import FindAccounts, RecurrentTransfer, SchemasAccount
    from clive.models.aliased import FindRecurrentTransfers as SchemasFindRecurrentTransfers
from clive.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node

AllowedBaseSorts = Literal[
    "amount",
    "from",
    "pair_id",
    "recurrence",
    "remaining_executions",
    "to",
    "trigger_date",
]

AllowedFutureSorts = Literal[
    AllowedBaseSorts,
    "possible_amount",
]

AllowedSorts = TypeVar("AllowedSorts", AllowedBaseSorts, AllowedFutureSorts)

LACK_OF_FUNDS_HBD_AMOUNT: Final[Asset.Hbd] = Asset.hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER)
LACK_OF_FUNDS_HIVE_AMOUNT: Final[Asset.Hive] = Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER)
LACK_OF_FUNDS: Final[list[Asset.Hbd | Asset.Hive]] = [LACK_OF_FUNDS_HBD_AMOUNT, LACK_OF_FUNDS_HIVE_AMOUNT]


class FindRecurrentTransferError(CommandError):
    pass


class FindRecurrentTransferFromAccountMismatchError(FindRecurrentTransferError):
    """Exception raised when there is account mismatch."""

    def __init__(self, command: Command, account_name: str, recurrent_transfer: RecurrentTransfer) -> None:
        self.account_name = account_name
        self.recurrent_transfer = recurrent_transfer
        self.reason = f"Wrong from account '{self.recurrent_transfer.from_}' should be '{self.account_name}'."
        super().__init__(command=command, reason=self.reason)


@dataclass
class _HarvestedDataRaw:
    recurrent_transfers: SchemasFindRecurrentTransfers
    account_data: FindAccounts


@dataclass
class _SanitizedData:
    recurrent_transfers: list[RecurrentTransfer]
    account_data: SchemasAccount


@dataclass
class ScheduledTransfer:
    amount: Asset.LiquidT
    consecutive_failures: int
    from_: str
    memo: str
    pair_id: int
    recurrence: int
    remaining_executions: int
    to: str
    trigger_date: datetime


@dataclass
class FutureScheduledTransfer:
    amount: Asset.LiquidT
    from_: str
    memo: str
    pair_id: int
    possible_amount: Asset.LiquidT
    recurrence: int
    remaining_executions: int
    to: str
    trigger_date: datetime

    def is_lack_of_funds(self) -> bool:
        return self.possible_amount in LACK_OF_FUNDS


TypeOfTransfers = ScheduledTransfer | FutureScheduledTransfer


def _assert_sort_by_members_in_class_members(sort_by: Sequence[str], of_class: type[TypeOfTransfers]) -> None:
    all_members = [field.name for field in fields(of_class)]
    assert all(member in all_members for member in sort_by), (
        f"Invalid sort_by member: `{sort_by}`. "
        f"Perhaps there is a bug in AllowedSorts literal? Allowed are `{all_members}`"
    )


@dataclass
class AccountScheduledTransferData:
    scheduled_transfers: list[ScheduledTransfer]
    account_hive_balance: Asset.Hive
    account_hbd_balance: Asset.Hbd

    def has_any_scheduled_transfers(self) -> bool:
        return bool(self.scheduled_transfers)

    def sorted_by(self, sort_by: list[AllowedBaseSorts], *, descending: bool = False) -> AccountScheduledTransferData:
        import operator

        _assert_sort_by_members_in_class_members(sort_by, ScheduledTransfer)

        return AccountScheduledTransferData(
            scheduled_transfers=sorted(self.scheduled_transfers, key=operator.attrgetter(*sort_by), reverse=descending),
            account_hive_balance=self.account_hive_balance,
            account_hbd_balance=self.account_hbd_balance,
        )

    def get_amount_aligned_to_dot(self, center_to: int | str | None = None) -> list[str]:
        return align_to_dot(
            *[humanize_asset(st.amount) for st in self.scheduled_transfers],
            center_to=center_to,
        )

    def calculate_possible_amount(self, balance: Asset.LiquidT, amount: Asset.LiquidT) -> Asset.LiquidT:
        lack_of_funds: Asset.LiquidT = LACK_OF_FUNDS_HIVE_AMOUNT if Asset.is_hive(amount) else LACK_OF_FUNDS_HBD_AMOUNT
        return balance - amount if balance > amount else lack_of_funds

    def get_next_upcoming_future_scheduled_transfers(self, next_upcoming: int) -> AccountFutureScheduledTransferData:
        future_scheduled_transfers: list[FutureScheduledTransfer] = []
        # Create all future scheduled transfers
        for st in self.scheduled_transfers:
            number_of_calculated_future_scheduled_transfers = min(st.remaining_executions, next_upcoming)
            future_scheduled_transfers.extend(
                FutureScheduledTransfer(
                    amount=st.amount,
                    from_=st.from_,
                    memo=st.memo,
                    pair_id=st.pair_id,
                    possible_amount=LACK_OF_FUNDS_HIVE_AMOUNT if Asset.is_hive(st.amount) else LACK_OF_FUNDS_HBD_AMOUNT,
                    recurrence=st.recurrence,
                    remaining_executions=remains,
                    to=st.to,
                    trigger_date=st.trigger_date + timedelta(hours=idx * st.recurrence),
                )
                for idx, remains in enumerate(range(number_of_calculated_future_scheduled_transfers))
            )

        # Sort future transfer list, and slice it to next_upcoming value
        future_scheduled_transfers.sort(key=lambda x: x.trigger_date)
        upcoming_future_transfers = future_scheduled_transfers[:next_upcoming]
        upcoming_future_transfers_data = AccountFutureScheduledTransferData(
            future_scheduled_transfers=upcoming_future_transfers
        )

        # Calculate possible amounts
        account_hive_balance = self.account_hive_balance
        account_hbd_balance = self.account_hbd_balance
        for future_transfer in upcoming_future_transfers_data.future_scheduled_transfers:
            if Asset.is_hive(future_transfer.amount):
                account_hive_balance = cast(
                    Asset.Hive, self.calculate_possible_amount(account_hive_balance, future_transfer.amount)
                )
                future_transfer.possible_amount = account_hive_balance
            else:
                account_hbd_balance = cast(
                    Asset.Hbd, self.calculate_possible_amount(account_hbd_balance, future_transfer.amount)
                )
                future_transfer.possible_amount = account_hbd_balance
        return upcoming_future_transfers_data


@dataclass
class AccountFutureScheduledTransferData:
    future_scheduled_transfers: list[FutureScheduledTransfer]

    def sorted_by(
        self, sort_by: list[AllowedFutureSorts], *, descending: bool = False
    ) -> AccountFutureScheduledTransferData:
        import operator

        _assert_sort_by_members_in_class_members(sort_by, FutureScheduledTransfer)

        return AccountFutureScheduledTransferData(
            future_scheduled_transfers=sorted(
                self.future_scheduled_transfers, key=operator.attrgetter(*sort_by), reverse=descending
            )
        )

    def get_amount_aligned_to_dot(self, center_to: int | str | None = None) -> list[str]:
        amount_to_align = [humanize_asset(ft.amount) for ft in self.future_scheduled_transfers]
        return align_to_dot(*amount_to_align, center_to=center_to)

    def get_possible_amount_aligned_to_dot(self, center_to: int | str | None = None) -> list[str]:
        possible_amount_to_align = [humanize_asset(ft.possible_amount) for ft in self.future_scheduled_transfers]
        return align_to_dot(*possible_amount_to_align, center_to=center_to)


@dataclass(kw_only=True)
class FindScheduledTransfers(CommandDataRetrieval[_HarvestedDataRaw, _SanitizedData, AccountScheduledTransferData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> _HarvestedDataRaw:
        async with self.node.batch() as node:
            return _HarvestedDataRaw(
                recurrent_transfers=await node.api.database_api.find_recurrent_transfers(from_=self.account_name),
                account_data=await node.api.database_api.find_accounts(accounts=[self.account_name]),
            )

    async def _sanitize_data(self, data: _HarvestedDataRaw) -> _SanitizedData:
        return _SanitizedData(
            recurrent_transfers=self._sanitize_recurrent_transfers(data.recurrent_transfers),
            account_data=self._sanitize_account_data(data.account_data),
        )

    async def _process_data(self, data: _SanitizedData) -> AccountScheduledTransferData:
        scheduled_transfers = [
            ScheduledTransfer(
                from_=rt.from_,
                to=rt.to,
                trigger_date=rt.trigger_date,
                amount=rt.amount,
                memo=rt.memo,
                recurrence=rt.recurrence,
                remaining_executions=rt.remaining_executions,
                pair_id=rt.pair_id,
                consecutive_failures=rt.consecutive_failures,
            )
            for rt in data.recurrent_transfers
        ]
        return AccountScheduledTransferData(
            account_hive_balance=data.account_data.balance,
            account_hbd_balance=data.account_data.hbd_balance,
            scheduled_transfers=scheduled_transfers,
        )

    def _sanitize_recurrent_transfers(self, data: SchemasFindRecurrentTransfers) -> list[RecurrentTransfer]:
        self._assert_from_account(data)
        return data.recurrent_transfers

    def _sanitize_account_data(self, data: FindAccounts) -> SchemasAccount:
        self._assert_account_data(data)
        return data.accounts[0]

    def _assert_account_data(self, data: FindAccounts) -> None:
        assert len(data.accounts) == 1, "Invalid amount of accounts."

        account = data.accounts[0]
        assert account.name == self.account_name, "Invalid account name"

    def _assert_from_account(self, data: SchemasFindRecurrentTransfers) -> None:
        for recurrent_transfer in data.recurrent_transfers:
            if recurrent_transfer.from_ != self.account_name:
                raise FindRecurrentTransferFromAccountMismatchError(
                    self, account_name=self.account_name, recurrent_transfer=recurrent_transfer
                )
