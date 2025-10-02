from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.constants.cli import (
    DEFAULT_AUTHORITY_THRESHOLD,
    DEFAULT_AUTHORITY_WEIGHT,
)
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import (
    AccountCreateOperation,
    Authority,
    CreateClaimedAccountOperation,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountWithWeight, KeyWithWeight
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.core.types import AuthorityLevelRegular


class MissingAuthorityError(CLIPrettyError):
    """
    Raised when trying to create a account without authority given as parameter.

    Args:
        level: A type of authority that is missing.
    """

    def __init__(self, level: AuthorityLevelRegular) -> None:
        super().__init__(f"There must be at least one key or account in {level} authority.")


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


def _create_empty_authority() -> Authority:
    return Authority(weight_threshold=DEFAULT_AUTHORITY_THRESHOLD, account_auths=[], key_auths=[])


@dataclass(kw_only=True)
class ProcessAccountCreation(OperationCommand):
    creator: str
    new_account_name: str
    fee: bool
    json_metadata: str
    _owner_authority: Authority = field(default_factory=_create_empty_authority)
    _active_authority: Authority = field(default_factory=_create_empty_authority)
    _posting_authority: Authority = field(default_factory=_create_empty_authority)
    _memo_key: PublicKey | None = None
    _fee_value: Asset.Hive | None = None  # Set after fetching from node

    @property
    def fee_value_ensure(self) -> Asset.Hive:
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
    def memo_key_ensure(self) -> PublicKey:
        assert self._memo_key is not None, "Memo key must be specified by user and set with method `set_memo_key`"
        return self._memo_key

    @property
    def is_memo_key_set(self) -> bool:
        return self._memo_key is not None

    def add_authority(
        self,
        level: AuthorityLevelRegular,
        threshold: int,
        keys_with_weight: list[KeyWithWeight],
        accounts_with_weight: list[AccountWithWeight],
    ) -> None:
        self._set_threshold(level, threshold)
        for key, weight in keys_with_weight:
            self._add_key_authority(level, key, weight)
        for account_name, weight in accounts_with_weight:
            self._add_account_authority(level, account_name, weight)

    @override
    async def fetch_data(self) -> None:
        if self.fee:
            witness_schedule = await self.world.node.api.database_api.get_witness_schedule()
            if witness_schedule.median_props.account_creation_fee is None:
                raise FetchAccountCreationFeeError
            self._fee_value = witness_schedule.median_props.account_creation_fee
            print_cli(f"Account creation fee: `{Asset.to_legacy(self._fee_value)}` will be paid.")
        else:
            self._fee_value = Asset.hive(0)

    def is_fee_given(self, *, fee: bool | None) -> bool:
        return fee is not None

    @override
    async def post_run(self) -> None:
        if not self.profile.accounts.is_account_known(self.new_account_name):
            print_cli(f"Adding account `{self.new_account_name}` to known accounts.")
            self.profile.accounts.add_known_account(self.new_account_name)

    def set_memo_key(self, key: PublicKey) -> None:
        self._memo_key = key

    def set_keys(self, owner: PublicKey, active: PublicKey, posting: PublicKey) -> None:
        for authority_type in ("owner", "active", "posting"):
            self._set_threshold(authority_type, DEFAULT_AUTHORITY_THRESHOLD)
            self._add_key_authority(
                authority_type,
                {
                    "owner": owner,
                    "active": active,
                    "posting": posting,
                }[authority_type],
                DEFAULT_AUTHORITY_WEIGHT,
            )

    @override
    async def validate(self) -> None:
        self._validate_all_authorities_are_set()
        await super().validate()

    def _add_key_authority(self, level: AuthorityLevelRegular, key: PublicKey, weight: int) -> None:
        self._get_authority(level).key_auths.append((key.value, weight))

    def _add_account_authority(self, level: AuthorityLevelRegular, account_name: str, weight: int) -> None:
        self._get_authority(level).account_auths.append((account_name, weight))

    async def _create_operation(self) -> AccountCreateOperation | CreateClaimedAccountOperation:
        if self.fee:
            return AccountCreateOperation(
                fee=self.fee_value_ensure,
                creator=self.creator,
                new_account_name=self.new_account_name,
                json_metadata=self.json_metadata,
                owner=self._owner_authority,
                active=self._active_authority,
                posting=self._posting_authority,
                memo_key=self.memo_key_ensure.value,
            )
        return CreateClaimedAccountOperation(
            creator=self.creator,
            new_account_name=self.new_account_name,
            json_metadata=self.json_metadata,
            owner=self._owner_authority,
            active=self._active_authority,
            posting=self._posting_authority,
            memo_key=self.memo_key_ensure.value,
        )

    def _get_authority(self, level: AuthorityLevelRegular) -> Authority:
        mapping: dict[AuthorityLevelRegular, Authority] = {
            "owner": self._owner_authority,
            "active": self._active_authority,
            "posting": self._posting_authority,
        }
        try:
            return mapping[level]
        except KeyError as err:
            raise ValueError(f"Unknown authority type: {level}") from err

    @staticmethod
    def _is_authority_set(auth: Authority) -> bool:
        return bool(auth.account_auths) or bool(auth.key_auths)

    def _set_threshold(self, level: AuthorityLevelRegular, threshold: int) -> None:
        self._get_authority(level).weight_threshold = threshold

    def _validate_all_authorities_are_set(self) -> None:
        if not self.is_owner_authority_set:
            raise MissingAuthorityError("owner")
        if not self.is_active_authority_set:
            raise MissingAuthorityError("active")
        if not self.is_posting_authority_set:
            raise MissingAuthorityError("posting")
        if not self.is_memo_key_set:
            raise MissingMemoKeyError
