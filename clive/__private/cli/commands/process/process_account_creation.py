from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, cast, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.constants.cli import (
    DEFAULT_AUTHORITY_THRESOHLD,
    DEFAULT_AUTHORITY_WEIGHT,
)
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import (
    AccountCreateOperation,
    AssetHive,
    Authority,
    CreateClaimedAccountOperation,
)
from clive.__private.models.schemas import PublicKey as SchemasPublicKey

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountWithWeight, KeyWithWeight
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.core.types import AuthorityLevelRegular


class MissingNewAccountNameOptionError(CLIPrettyError):
    """
    Raised when option '--new-account-name` is missing.

    Attributes:
        MESSAGE: A message displayed to user when this error occurs.
    """

    MESSAGE: Final[str] = "Missing option '--new-account-name'."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class MissingAuthorityError(CLIPrettyError):
    """
    Raised when trying to create a account without authority given as parameter.

    Args:
        type_: A type of authority that is missing.
    """

    def __init__(self, type_: AuthorityLevelRegular) -> None:
        super().__init__(MissingAuthorityError.create_message(type_))

    @staticmethod
    def create_message(type_: AuthorityLevelRegular) -> str:
        return f"There must be at least one key or account in {type_} authority."


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
    new_account_name: str | None
    fee: bool | None = None
    json_metadata: str | None = None
    _owner_authority: Authority = field(
        default_factory=lambda: Authority(weight_threshold=DEFAULT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[])
    )
    _active_authority: Authority = field(
        default_factory=lambda: Authority(weight_threshold=DEFAULT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[])
    )
    _posting_authority: Authority = field(
        default_factory=lambda: Authority(weight_threshold=DEFAULT_AUTHORITY_THRESOHLD, account_auths=[], key_auths=[])
    )
    _memo_key: SchemasPublicKey | None = None
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
    def json_metadata_ensure(self) -> str:
        assert self.json_metadata is not None, (
            "Json medatata should be set to default value of empty string if not given explicitly"
        )
        return self.json_metadata

    @property
    def memo_key_ensure(self) -> SchemasPublicKey:
        assert self._memo_key is not None, "Memo key must be specified by user and set with method `set_memo_key`"
        return self._memo_key

    @property
    def new_account_name_ensure(self) -> str:
        assert self.new_account_name is not None, (
            "New account must be specified in command `clive process account-creation` or subcommands"
        )
        return self.new_account_name

    def add_key_authority(self, type_: AuthorityLevelRegular, key: PublicKey, weight: int) -> None:
        self._get_authority(type_).key_auths.append((key.value, weight))

    def add_account_authority(self, type_: AuthorityLevelRegular, account_name: str, weight: int) -> None:
        self._get_authority(type_).account_auths.append((account_name, weight))

    def add_authority(
        self,
        type_: AuthorityLevelRegular,
        threshold: int,
        keys_with_weight: list[KeyWithWeight],
        accounts_with_weight: list[AccountWithWeight],
    ) -> None:
        self.set_threshold(type_, threshold)
        for key, weight in keys_with_weight:
            self.add_key_authority(type_, key, weight)
        for account_name, weight in accounts_with_weight:
            self.add_account_authority(type_, account_name, weight)

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

    def modify_account_creation_common_options(  # noqa: PLR0913
        self,
        new_account_name: str | None = None,
        fee: bool | None = None,  # noqa: FBT001
        json_metadata: str | None = None,
        sign_with: str | None = None,
        autosign: bool | None = None,  # noqa: FBT001
        broadcast: bool | None = None,  # noqa: FBT001
        save_file: str | None = None,
    ) -> None:
        is_new_account_name_given = new_account_name is not None
        is_fee_given = fee is not None
        is_json_metadata_given = json_metadata is not None

        if is_new_account_name_given:
            self.new_account_name = cast("str", new_account_name)

        if is_fee_given:
            self.fee = cast("bool", fee)

        if is_json_metadata_given:
            self.json_metadata = cast("str", json_metadata)

        self.modify_common_options(
            sign_with=sign_with,
            autosign=autosign,
            broadcast=broadcast,
            save_file=save_file,
        )

    def set_threshold(self, type_: AuthorityLevelRegular, threshold: int) -> None:
        self._get_authority(type_).weight_threshold = threshold

    def set_memo_key(self, key: PublicKey) -> None:
        self._memo_key = key.value

    def set_keys(self, owner: PublicKey, active: PublicKey, posting: PublicKey) -> None:
        for authority_type in ("owner", "active", "posting"):
            self.set_threshold(authority_type, DEFAULT_AUTHORITY_THRESOHLD)
            self.add_key_authority(
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
        if self.new_account_name is None:
            print_cli("[yellow]Usage:[/] clive process account-creation [OPTIONS]")
            command_path = "clive process account-creation"
            help_option = "-h"
            print_cli(f"[dim]Try [blue]'{command_path} {help_option}'[/] for help.[/]")
            raise MissingNewAccountNameOptionError
        if not self.is_owner_authority_set:
            raise MissingAuthorityError("owner")
        if not self.is_active_authority_set:
            raise MissingAuthorityError("active")
        if not self.is_posting_authority_set:
            raise MissingAuthorityError("posting")
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
                new_account_name=self.new_account_name_ensure,
                owner=self._owner_authority,
                active=self._active_authority,
                posting=self._posting_authority,
                memo_key=self.memo_key_ensure,
                json_metadata=self.json_metadata_ensure,
            )
        return CreateClaimedAccountOperation(
            creator=self.creator,
            new_account_name=self.new_account_name_ensure,
            owner=self._owner_authority,
            active=self._active_authority,
            posting=self._posting_authority,
            memo_key=self.memo_key_ensure,
            json_metadata=self.json_metadata_ensure,
        )

    async def _configure(self) -> None:
        if self.fee is None:
            self.fee = False
        if self.json_metadata is None:
            self.json_metadata = ""
        await super()._configure()

    def _get_authority(self, type_: AuthorityLevelRegular) -> Authority:
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
        if not self.profile.accounts.is_account_known(self.new_account_name_ensure):
            print_cli(f"Adding account `{self.new_account_name_ensure}` to known accounts.")
            self.profile.accounts.add_known_account(self.new_account_name_ensure)
