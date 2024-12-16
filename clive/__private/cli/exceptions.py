from __future__ import annotations

import errno
from typing import TYPE_CHECKING, Final

from click import ClickException

from clive.__private.core.constants.node import (
    PERCENT_TO_REMOVE_WITHDRAW_ROUTE,
    SCHEDULED_TRANSFER_MAX_LIFETIME,
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
    VESTS_TO_REMOVE_DELEGATION,
)
from clive.__private.core.formatters.humanize import humanize_timedelta
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.profile import Profile


from clive.__private.core.constants.setting_identifiers import BEEKEEPER_REMOTE_ADDRESS, BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar

BEEKEEPER_PASSWORD_OR_SESSION_TOKEN_MUST_BE_SET_MESSAGE: Final[str] = (
    "You must provide a password or a beekeeper unlocked session token set via envvar"
)


class CLIPrettyError(ClickException):
    """
    A pretty error to be shown to the user.

    Example:
    -------
    >>> raise CLIPrettyError("some message")
    ╭─ Error ───────────────────────────────────────────────────╮
    │ some message                                              │
    ╰───────────────────────────────────────────────────────────╯
    """

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class CLIWorkingAccountIsNotSetError(CLIPrettyError):
    def __init__(self, profile: Profile | None = None) -> None:
        self.profile = profile
        message = (
            f"Working account is not set{f' for the `{profile.name}` profile' if profile else ''}.\n"
            "Please check the `clive configure working-account add -h` command first."
        )
        super().__init__(message, errno.ENOENT)


class CLIWorkingAccountIsAlreadySetError(CLIPrettyError):
    def __init__(self, profile: Profile | None = None) -> None:
        self.profile = profile
        message = (
            f"Working account is already set{f' for the `{profile.name}` profile' if profile else ''}.\n"
            "If you want to change the working account - please check the `clive configure working-account -h` command."
        )
        super().__init__(message, errno.EEXIST)


class CLIProfileDoesNotExistsError(CLIPrettyError):
    def __init__(self, profile_name: str | None = None) -> None:
        self.profile_name = profile_name
        detail = f" `{profile_name}` " if profile_name else " "
        message = (
            f"Profile{detail}does not exist.\n"
            "Please check the `clive show profiles` command first.\n"
            "If you want to create a new profile - please check the `clive configure profile add -h` command."
        )
        super().__init__(message, errno.EEXIST)


class CLIProfileAlreadyExistsError(CLIPrettyError):
    def __init__(self, profile_name: str | None = None, existing_profiles: list[str] | None = None) -> None:
        self.profile_name = profile_name
        self.existing_profiles = existing_profiles

        profile_name_detail = f" `{profile_name}` " if profile_name else " "
        existing_profiles_detail = f", different than {existing_profiles}." if existing_profiles else "."
        message = (
            f"Profile{profile_name_detail}already exists. Please choose another name{existing_profiles_detail}\n"
            "If you want to create a new profile - please check the `clive configure profile add -h` command."
        )
        super().__init__(message, errno.EEXIST)


class CLIBothBeekeepersPasswordAndSessionTokenSetError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            f"Both '--password' flag and environment variable {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)} are set."
            " Please use only one."
        )
        super().__init__(message, errno.EINVAL)


class CLIEitherBeekeepersPasswordOrSessionTokenNotSetError(CLIPrettyError):
    def __init__(self) -> None:
        message = BEEKEEPER_PASSWORD_OR_SESSION_TOKEN_MUST_BE_SET_MESSAGE
        super().__init__(message, errno.EINVAL)


class CLIWalletIsNotUnlockedError(CLIPrettyError):
    def __init__(self, name: str) -> None:
        self.name = name
        env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
        message = f"If you want to use {env_var} envvar, ensure it is in unlocked state for wallet {self.name}."
        super().__init__(message, errno.EINVAL)


class CLISigningRequiresAPasswordOrSessionTokenError(CLIPrettyError):
    def __init__(self) -> None:
        message = f"{BEEKEEPER_PASSWORD_OR_SESSION_TOKEN_MUST_BE_SET_MESSAGE} to sign the transaction with."
        super().__init__(message, errno.EINVAL)


class CLIBroadcastCannotBeUsedWithForceUnsignError(CLIPrettyError):
    def __init__(self) -> None:
        message = "You cannot broadcast a transaction and force-unsign it at the same time."
        super().__init__(message, errno.EINVAL)


class PowerDownInProgressError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            "Power-down is already in progress, if you want to discard existing power-down and create new then use"
            " command `clive process power-down restart`"
        )
        super().__init__(message, errno.EPERM)


class WithdrawRoutesZeroPercentError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            f"Withdraw routes can't have {PERCENT_TO_REMOVE_WITHDRAW_ROUTE} percent, "
            "if you want to remove withdraw route then use command `clive process withdraw-routes remove`"
        )
        super().__init__(message, errno.EPERM)


class DelegationsZeroAmountError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            f"Delegation amount can't be {VESTS_TO_REMOVE_DELEGATION}, "
            "if you want to remove delegation then use command `clive process delegations remove`"
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleAlreadyExistsError(CLIPrettyError):
    def __init__(self, to: str, pair_id: int) -> None:
        self.to = to
        self.pair_id = pair_id
        message = (
            f"Scheduled transfer to `{self.to}` with pair_id `{self.pair_id}` already exists.\n"
            "Please use command `clive process transfer-schedule modify` to change it, "
            "or command `clive process transfer-schedule remove` to delete it."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleDoesNotExistsError(CLIPrettyError):
    def __init__(self, to: str, pair_id: int) -> None:
        self.to = to
        self.pair_id = pair_id
        message = (
            f"Scheduled transfer to `{self.to}` with pair_id `{self.pair_id}` does not exists.\n"
            f"Please create it first by using `clive process transfer-schedule create` command."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleInvalidAmountError(CLIPrettyError):
    def __init__(self) -> None:
        hive_symbol = Asset.get_symbol(Asset.Hive)
        hbd_symbol = Asset.get_symbol(Asset.Hbd)
        message = (
            "Amount for `clive process transfer-schedule create` or `clive process transfer-schedule modify` "
            f"commands must be greater than {VALUE_TO_REMOVE_SCHEDULED_TRANSFER} {hive_symbol}/{hbd_symbol}.\n"
            "If you want to remove scheduled transfer, please use `clive process transfer-schedule remove` command."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleNullPairIdError(CLIPrettyError):
    def __init__(self) -> None:
        message = "Pair id must be set explicit, when there are multiple scheduled transfers defined."
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleTooLongLifetimeError(CLIPrettyError):
    def __init__(self, requested_lifetime: timedelta) -> None:
        self.requested_lifetime = requested_lifetime
        message = (
            f"Requested lifetime of scheduled transfer is too long ({humanize_timedelta(self.requested_lifetime)}).\n"
            f"Maximum available lifetime is {humanize_timedelta(SCHEDULED_TRANSFER_MAX_LIFETIME)}."
        )
        super().__init__(message, errno.EPERM)


class CLIBeekeeperSessionTokenIsNotSetError(CLIPrettyError):
    def __init__(self) -> None:
        token_env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
        address_env_var = clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)
        message = (
            f"Beekeeper session token is not set, you can set it with environment variable `{token_env_var}`"
            f" or with setting `{BEEKEEPER_SESSION_TOKEN}` in settings file. Variable `{address_env_var}`"
            f" or setting `{BEEKEEPER_REMOTE_ADDRESS}` is also required."
        )
        super().__init__(message, errno.ENOENT)


class CLIInvalidPasswordError(CLIPrettyError):
    def __init__(self, profile_name: str) -> None:
        message = f"Password for profile `{profile_name}` is incorrect."
        super().__init__(message, errno.EPERM)


class CLISessionNotLockedError(CLIPrettyError):
    def __init__(self) -> None:
        message = "All wallets in session should be locked."
        super().__init__(message, errno.EPERM)


class CLIInvalidSelectionError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Invalid selection.", errno.EINVAL)


class CLIBeekeeperRemoteAddressIsNotSetError(CLIPrettyError):
    def __init__(self) -> None:
        token_env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
        address_env_var = clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)
        message = (
            f"Beekeeper remote address is not set, you can set it with environment variable `{address_env_var}`"
            f" or with setting `{BEEKEEPER_REMOTE_ADDRESS}` in settings file. Variable `{token_env_var}`"
            f" or setting `{BEEKEEPER_SESSION_TOKEN}` is also required."
        )
        super().__init__(message, errno.ENOENT)


class CLIBeekeeperInstanceAlreadyRunningError(CLIPrettyError):
    def __init__(self, address: str, pid: int) -> None:
        self.address = address
        self.pid = pid
        message = f"Beekeeper is already running on {address} with pid {pid}"
        super().__init__(message)


class CLIBeekeeperDanglingPidError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            "An error occurs while setting up Beekeeper, apparently Beekeeper didn't close properly and left"
            " dangling pid file."
        )
        super().__init__(message)
