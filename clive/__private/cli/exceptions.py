from __future__ import annotations

import errno
from typing import TYPE_CHECKING, Final

from click import ClickException

from clive.__private.core.constants.node import (
    PERCENT_TO_REMOVE_WITHDRAW_ROUTE,
    SCHEDULED_TRANSFER_MAX_LIFETIME,
)
from clive.__private.core.constants.node_special_assets import (
    DELEGATION_REMOVE_ASSETS,
    SCHEDULED_TRANSFER_REMOVE_ASSETS,
)
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_REMOTE_ADDRESS, BEEKEEPER_SESSION_TOKEN
from clive.__private.core.formatters.humanize import humanize_asset, humanize_timedelta
from clive.__private.settings import clive_prefixed_envvar

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy.interfaces import HttpUrl

    from clive.__private.core.profile import Profile


class CLIPrettyError(ClickException):
    """
    A pretty error to be shown to the user.

    Args:
        message: The error message to be shown.
        exit_code: The exit code to be used when exiting the program.

    Example:
        >>> raise CLIPrettyError("some message")
        ╭─ Error ───────────────────────────────────────────────────╮
        │ some message                                              │
        ╰───────────────────────────────────────────────────────────╯
    """

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


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


class CLIBeekeeperSessionTokenNotSetError(CLIPrettyError):
    MESSAGE: Final[str] = "The session token is not set. Please run via start_clive_cli.sh."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE, errno.EINVAL)


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
        remove_assets = " or ".join(humanize_asset(asset) for asset in DELEGATION_REMOVE_ASSETS)
        message = (
            f"Delegation amount can't be {remove_assets}, "
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
        remove_assets = " or ".join(humanize_asset(asset) for asset in SCHEDULED_TRANSFER_REMOVE_ASSETS)
        message = (
            "Amount for `clive process transfer-schedule create` or `clive process transfer-schedule modify` "
            f"commands must be greater than {remove_assets}.\n"
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


class CLIInvalidPasswordError(CLIPrettyError):
    def __init__(self, profile_name: str) -> None:
        message = f"Password for profile `{profile_name}` is incorrect."
        super().__init__(message, errno.EPERM)


class CLIInvalidPasswordRepeatError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            "Repeated password doesn't match previously entered password."
            " The profile was not created. Please try again."
        )
        super().__init__(message, errno.EPERM)


class CLISessionNotLockedError(CLIPrettyError):
    def __init__(self) -> None:
        message = "All wallets in session should be locked."
        super().__init__(message, errno.EPERM)


class CLIInvalidSelectionError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Invalid selection.", errno.EINVAL)


class CLIBeekeeperRemoteAddressIsNotSetError(CLIPrettyError):
    MESSAGE: Final[str] = "Beekeeper remote address is not set. Please run via start_clive_cli.sh."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE, errno.EINVAL)


class CLINoProfileUnlockedError(CLIPrettyError):
    MESSAGE: Final[str] = "There is no unlocked profile on the beekeeper. Perform `clive unlock` command first."

    def __init__(self) -> None:
        super().__init__(self.MESSAGE, errno.EACCES)


class CLICreatingProfileCommunicationError(CLIPrettyError):
    MESSAGE: Final[str] = (
        "Profile can't be created because communication with beekeeper failed.\n"
        "Maybe wallet with this name already exists."
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE, errno.EEXIST)


class CLIBeekeeperRemoteAddressIsNotRespondingError(CLIPrettyError):
    def __init__(self, url: HttpUrl) -> None:
        message = f"Beekeeper on address {url} is not responding."
        super().__init__(message, errno.EEXIST)


class CLIBeekeeperLocallyAlreadyRunningError(CLIPrettyError):
    def __init__(self, pid: int) -> None:
        message = f"Local instance of Beekeeper is already running with pid {pid}"
        super().__init__(message, errno.EEXIST)


class CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            "Cannot spawn new instance of Beekeepeer while "
            f"the env variable of {clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)} "
            f"or {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)} is set.\n"
            "If you wish to launch Beekeeper locally, please unset them first, then retry with `clive beekeeper spawn`."
        )
        super().__init__(message, errno.EEXIST)


class CLITransactionNotSignedError(CLIPrettyError):
    """Raise when trying to broadcast unsigned transaction."""

    MESSAGE: Final[str] = "Could not broadcast unsigned transaction. Did you forget the '--sign' option?"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE, errno.EINVAL)


class CLITransactionUnknownAccountError(CLIPrettyError):
    """Raise when trying to perform transaction with operation(s) to unknown account."""

    def __init__(self, *account_names: str) -> None:
        assert account_names, (
            "At least one account name must be provided for CLITransactionUnknownAccountError exception."
        )
        self.account_names = list(account_names)

        message = (
            "Clive cannot perform the transaction because the "
            f"target accounts: {self.account_names} are not on the list of known accounts.\n"
            "To perform the transaction, add the target accounts to the list of known accounts.\n"
            f"You can do this using the command: `clive configure known-account add {self.account_names[0]}`.\n"
            "You have to repeat this command for each account that is not on the list of known accounts.\n"
            "For more information about the known-account feature, see `clive configure known-account -h`."
        )
        super().__init__(message, errno.EINVAL)


class CLITransactionBadAccountError(CLIPrettyError):
    """Raise when trying to perform transaction with operation(s) to bad account."""

    def __init__(self, *account_names: str) -> None:
        self.account_names = list(account_names)

        message = (
            "Clive cannot perform the transaction because the "
            f"target accounts: {self.account_names} are on the list of bad accounts."
        )
        super().__init__(message, errno.EINVAL)


class CLITransactionToExchangeError(CLIPrettyError):
    """Raise when trying to perform transaction to exchange with operation(s) that cannot be performed."""

    def __init__(self, reason: str) -> None:
        message = f"Cannot perform transaction.\n{reason}"
        super().__init__(message, errno.EINVAL)
        self.message = message
