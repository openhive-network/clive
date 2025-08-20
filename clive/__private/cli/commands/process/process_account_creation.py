from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, override

import typer

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.cli import NEW_ACCOUNT_AUTHORITY_THRESOHLD
from clive.__private.models.schemas import (
    AccountCreateOperation,
    AssetHive,
    Authority,
    CreateClaimedAccountOperation,
    PublicKey,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import AuthorityType


class NoChangesTransactionError(CLIPrettyError):
    """
    Raised when trying to create a transaction with no changes to authority.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "Transaction with no changes to authority cannot be created."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


@dataclass(kw_only=True)
class ProcessAccountCreation(OperationCommand):
    creator: str
    new_account_name: str
    fee: bool
    json_metadata: str

    _owner_authority: Authority = field(
        default_factory=lambda: Authority(
            weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[]
        )
    )
    _active_authority: Authority = field(
        default_factory=lambda: Authority(
            weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[]
        )
    )
    _posting_authority: Authority = field(
        default_factory=lambda: Authority(
            weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[]
        )
    )
    _memo_key: PublicKey = field(init=False)
    _fee_value: AssetHive = field(init=False)

    @override
    async def fetch_data(self) -> None:
        if self.fee:
            witness_schedule = await self.world.node.api.database_api.get_witness_schedule()
            if witness_schedule.median_props.account_creation_fee is None:
                raise CLIPrettyError("Could not fetch account creation fee from the network")
            self._fee_value = witness_schedule.median_props.account_creation_fee
            typer.echo(f"Accountt creation fee `{self._fee_value}` will be paid.")
        else:
            self._fee_value = AssetHive(0)

    @override
    async def validate(self) -> None:
        if not hasattr(self, "_memo_key"):
            raise CLIPrettyError("Memo key must be set before creating account")
        await super().validate()

    @override
    async def validate_inside_context_manager(self) -> None:
        assert hasattr(self, "_fee_value"), "_fee_value not initialized"
        await super().validate_inside_context_manager()

    async def _create_operation(self) -> AccountCreateOperation | CreateClaimedAccountOperation:
        if self.fee:
            return AccountCreateOperation(
                fee=self._fee_value,
                creator=self.creator,
                new_account_name=self.new_account_name,
                owner=self._owner_authority,
                active=self._active_authority,
                posting=self._posting_authority,
                memo_key=self._memo_key,
                json_metadata=self.json_metadata,
            )
        return CreateClaimedAccountOperation(
            creator=self.creator,
            new_account_name=self.new_account_name,
            owner=self._owner_authority,
            active=self._active_authority,
            posting=self._posting_authority,
            memo_key=self._memo_key,
            json_metadata=self.json_metadata,
        )

    async def _run(self) -> None:
        await super()._run()
        typer.echo(f"Adding account `{self.new_account_name}` to known accounts.")
        if self.broadcast:
            self.profile.accounts.add_known_account(self.new_account_name)

    def _get_authority(self, type_: AuthorityType) -> Authority:
        if type_ == "owner":
            return self._owner_authority
        if type_ == "active":
            return self._active_authority
        if type_ == "posting":
            return self._posting_authority
        raise ValueError(f"Unknown authority type: {type_}")

    def add_key_authority(self, type_: AuthorityType, key: PublicKey, weight: int) -> None:
        self._get_authority(type_).key_auths.append((key, weight))

    def add_account_authority(self, type_: AuthorityType, key: PublicKey, weight: int) -> None:
        self._get_authority(type_).account_auths.append((key, weight))

    def set_threshold(self, type_: AuthorityType, threshold: int) -> None:
        self._get_authority(type_).weight_threshold = threshold

    def set_memo_key(self, key: PublicKey) -> None:
        self._memo_key = key
