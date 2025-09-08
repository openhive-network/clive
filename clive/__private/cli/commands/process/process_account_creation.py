from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.constants.cli import NEW_ACCOUNT_AUTHORITY_THRESOHLD
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import (
    AccountCreateOperation,
    AssetHive,
    Authority,
    CreateClaimedAccountOperation,
    PublicKey,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import AuthorityType


class MissingOwnerAuthorityError(CLIPrettyError):
    """
    Raised when trying to create a account without owner authority.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "There must be at least one key or account in owner authority."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class MissingActiveAuthorityError(CLIPrettyError):
    """
    Raised when trying to create a account without active authority.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "There must be at least one key or account in active authority."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class MissingPostingAuthorityError(CLIPrettyError):
    """
    Raised when trying to create a account without posting authority.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "There must be at least one key or account in posting authority."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class MissingMemoKeyError(CLIPrettyError):
    """
    Raised when trying to create a account without memo key.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "Memo key must be set when creating account."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class FetchAccountCreationFeeError(CLIPrettyError):
    """
    Raised when failed to fetch account creation fe from node.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = (
        "Could not fetch account creation fee from the node."
        " You can display node with command `clive show node` and set node with command `clive configure node set`."
    )

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
    _memo_key: PublicKey | None = None
    _fee_value: AssetHive | None = None  # Set after fetching from node

    @property
    def fee_value_ensure(self) -> AssetHive:
        assert self._fee_value is not None, "Value of fee must be fetched from node"
        return self._fee_value

    @property
    def is_active_authority_set(self) -> bool:
        return self._is_authority_set(self._active_authority)

    @property
    def is_owner_authority_set(self) -> bool:
        return self._is_authority_set(self._owner_authority)

    @property
    def is_posting_authority_set(self) -> bool:
        return self._is_authority_set(self._posting_authority)

    @property
    def is_memo_key_set(self) -> bool:
        return self._memo_key is not None

    @property
    def memo_key_ensure(self) -> PublicKey:
        assert self._memo_key is not None, "Memo key must be specified by user and set with method `set_memo_key`"
        return self._memo_key

    def add_key_authority(self, type_: AuthorityType, key: PublicKey, weight: int) -> None:
        self._get_authority(type_).key_auths.append((key, weight))

    def add_account_authority(self, type_: AuthorityType, account_name: str, weight: int) -> None:
        self._get_authority(type_).account_auths.append((account_name, weight))

    @override
    async def fetch_data(self) -> None:
        if self.fee:
            witness_schedule = await self.world.node.api.database_api.get_witness_schedule()
            if witness_schedule.median_props.account_creation_fee is None:
                raise FetchAccountCreationFeeError
            self._fee_value = witness_schedule.median_props.account_creation_fee
            print_cli(f"Account creation fee: `{Asset.to_legacy(self._fee_value)}` will be paid.")
        else:
            self._fee_value = AssetHive(0)

    def set_threshold(self, type_: AuthorityType, threshold: int) -> None:
        self._get_authority(type_).weight_threshold = threshold

    def set_memo_key(self, key: PublicKey) -> None:
        self._memo_key = key

    @override
    async def validate(self) -> None:
        if not self.is_owner_authority_set:
            raise MissingOwnerAuthorityError
        if not self.is_active_authority_set:
            raise MissingActiveAuthorityError
        if not self.is_posting_authority_set:
            raise MissingPostingAuthorityError
        if not self.is_memo_key_set:
            raise MissingMemoKeyError
        await super().validate()

    @override
    async def validate_inside_context_manager(self) -> None:
        await super().validate_inside_context_manager()

    async def _create_operation(self) -> AccountCreateOperation | CreateClaimedAccountOperation:
        if self.fee:
            return AccountCreateOperation(
                fee=self.fee_value_ensure,
                creator=self.creator,
                new_account_name=self.new_account_name,
                owner=self._owner_authority,
                active=self._active_authority,
                posting=self._posting_authority,
                memo_key=self.memo_key_ensure,
                json_metadata=self.json_metadata,
            )
        return CreateClaimedAccountOperation(
            creator=self.creator,
            new_account_name=self.new_account_name,
            owner=self._owner_authority,
            active=self._active_authority,
            posting=self._posting_authority,
            memo_key=self.memo_key_ensure,
            json_metadata=self.json_metadata,
        )

    def _get_authority(self, type_: AuthorityType) -> Authority:
        if type_ == "owner":
            return self._owner_authority
        if type_ == "active":
            return self._active_authority
        if type_ == "posting":
            return self._posting_authority
        raise ValueError(f"Unknown authority type: {type_}")

    @staticmethod
    def _is_authority_set(auth: Authority) -> bool:
        return bool(auth.account_auths) or bool(auth.key_auths)

    async def _run(self) -> None:
        await super()._run()
        if not self.profile.accounts.is_account_known(self.new_account_name):
            print_cli(f"Adding account `{self.new_account_name}` to known accounts.")
            self.profile.accounts.add_known_account(self.new_account_name)
