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

    <pre>
    Examples:
        >>> raise CLIPrettyError("some message")
        >>> ╭─ Error ───────────────────────────────────────────────────╮
        >>> │ some message                                              │
        >>> ╰───────────────────────────────────────────────────────────╯
    </pre>
    """

    def __init__(self, message: str, exit_code: int = 1) -> None:
        """
        Initialize the CLIPrettyError with a message and an exit code.

        Args:
            message: The error message to display.
            exit_code: The exit code to return when the error is raised. Defaults to 1.

        Returns:
            None
        """
        super().__init__(message)
        self.exit_code = exit_code


class CLIWorkingAccountIsAlreadySetError(CLIPrettyError):
    """Raise when trying to set working account while it is already set."""

    def __init__(self, profile: Profile | None = None) -> None:
        """
        Initialize the CLIWorkingAccountIsAlreadySetError with a profile.

        Args:
            profile: The profile for which the working account is already set. Defaults to None.

        Returns:
            None
        """
        self.profile = profile
        message = (
            f"Working account is already set{f' for the `{profile.name}` profile' if profile else ''}.\n"
            "If you want to change the working account - please check the `clive configure working-account -h` command."
        )
        super().__init__(message, errno.EEXIST)


class CLIProfileDoesNotExistsError(CLIPrettyError):
    """Raise when trying to use a profile that does not exist."""

    def __init__(self, profile_name: str | None = None) -> None:
        """
        Initialize the CLIProfileDoesNotExistsError with a profile name.

        Args:
            profile_name: The name of the profile that does not exist. Defaults to None.

        Returns:
            None
        """
        self.profile_name = profile_name
        detail = f" `{profile_name}` " if profile_name else " "
        message = (
            f"Profile{detail}does not exist.\n"
            "Please check the `clive show profiles` command first.\n"
            "If you want to create a new profile - please check the `clive configure profile add -h` command."
        )
        super().__init__(message, errno.EEXIST)


class CLIProfileAlreadyExistsError(CLIPrettyError):
    """Raise when trying to create a profile that already exists."""

    def __init__(self, profile_name: str | None = None, existing_profiles: list[str] | None = None) -> None:
        """
        Initialize the CLIProfileAlreadyExistsError with a profile name and existing profiles.

        Args:
            profile_name: The name of the profile that already exists. Defaults to None.
            existing_profiles: A list of existing profiles. Defaults to None.

        Returns:
            None
        """
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
    """Raise when trying to use CLI without a session token set."""

    MESSAGE: Final[str] = "The session token is not set. Please run via start_clive_cli.sh."

    def __init__(self) -> None:
        """
        Initialize the CLIBeekeeperSessionTokenNotSetError.

        Returns:
            None
        """
        super().__init__(self.MESSAGE, errno.EINVAL)


class CLIBroadcastCannotBeUsedWithForceUnsignError(CLIPrettyError):
    """Raise when trying to broadcast a transaction and force-unsign it at the same time."""

    def __init__(self) -> None:
        """
        Initialize the CLIBroadcastCannotBeUsedWithForceUnsignError.

        Returns:
            None
        """
        message = "You cannot broadcast a transaction and force-unsign it at the same time."
        super().__init__(message, errno.EINVAL)


class PowerDownInProgressError(CLIPrettyError):
    """Raise when trying to start a power-down while one is already in progress."""

    def __init__(self) -> None:
        """
        Initialize the PowerDownInProgressError.

        Returns:
            None
        """
        message = (
            "Power-down is already in progress, if you want to discard existing power-down and create new then use"
            " command `clive process power-down restart`"
        )
        super().__init__(message, errno.EPERM)


class WithdrawRoutesZeroPercentError(CLIPrettyError):
    """Raise when trying to create or modify withdraw routes with 0%."""

    def __init__(self) -> None:
        """
        Initialize the WithdrawRoutesZeroPercentError.

        Returns:
            None
        """
        message = (
            f"Withdraw routes can't have {PERCENT_TO_REMOVE_WITHDRAW_ROUTE} percent, "
            "if you want to remove withdraw route then use command `clive process withdraw-routes remove`"
        )
        super().__init__(message, errno.EPERM)


class DelegationsZeroAmountError(CLIPrettyError):
    """Raise when trying to create or modify delegations with 0 amount."""

    def __init__(self) -> None:
        """
        Initialize the DelegationsZeroAmountError.

        Returns:
            None
        """
        remove_assets = " or ".join(humanize_asset(asset) for asset in DELEGATION_REMOVE_ASSETS)
        message = (
            f"Delegation amount can't be {remove_assets}, "
            "if you want to remove delegation then use command `clive process delegations remove`"
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleAlreadyExistsError(CLIPrettyError):
    """Raise when trying to create a scheduled transfer that already exists."""

    def __init__(self, to: str, pair_id: int) -> None:
        """
        Initialize the ProcessTransferScheduleAlreadyExistsError with a recipient and pair_id.

        Args:
            to: The recipient of the scheduled transfer.
            pair_id: The pair_id of the scheduled transfer.

        Returns:
            None
        """
        self.to = to
        self.pair_id = pair_id
        message = (
            f"Scheduled transfer to `{self.to}` with pair_id `{self.pair_id}` already exists.\n"
            "Please use command `clive process transfer-schedule modify` to change it, "
            "or command `clive process transfer-schedule remove` to delete it."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleDoesNotExistsError(CLIPrettyError):
    """Raise when trying to modify or remove a scheduled transfer that does not exist."""

    def __init__(self, to: str, pair_id: int) -> None:
        """
        Initialize the ProcessTransferScheduleDoesNotExistsError with a recipient and pair_id.

        Args:
            to: The recipient of the scheduled transfer.
            pair_id: The pair_id of the scheduled transfer.

        Returns:
            None
        """
        self.to = to
        self.pair_id = pair_id
        message = (
            f"Scheduled transfer to `{self.to}` with pair_id `{self.pair_id}` does not exists.\n"
            f"Please create it first by using `clive process transfer-schedule create` command."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleInvalidAmountError(CLIPrettyError):
    """Raise when trying to create or modify a scheduled transfer with an invalid amount."""

    def __init__(self) -> None:
        """
        Initialize the ProcessTransferScheduleInvalidAmountError.

        Returns:
            None
        """
        remove_assets = " or ".join(humanize_asset(asset) for asset in SCHEDULED_TRANSFER_REMOVE_ASSETS)
        message = (
            "Amount for `clive process transfer-schedule create` or `clive process transfer-schedule modify` "
            f"commands must be greater than {remove_assets}.\n"
            "If you want to remove scheduled transfer, please use `clive process transfer-schedule remove` command."
        )
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleNullPairIdError(CLIPrettyError):
    """Raise when trying to create a scheduled transfer without setting pair_id."""

    def __init__(self) -> None:
        """
        Initialize the ProcessTransferScheduleNullPairIdError.

        Returns:
            None
        """
        message = "Pair id must be set explicit, when there are multiple scheduled transfers defined."
        super().__init__(message, errno.EPERM)


class ProcessTransferScheduleTooLongLifetimeError(CLIPrettyError):
    """Raise when trying to create a scheduled transfer with a lifetime longer than the maximum allowed."""

    def __init__(self, requested_lifetime: timedelta) -> None:
        """
        Initialize the ProcessTransferScheduleTooLongLifetimeError with the requested lifetime.

        Args:
            requested_lifetime: The requested lifetime for the scheduled transfer.

        Returns:
            None
        """
        self.requested_lifetime = requested_lifetime
        message = (
            f"Requested lifetime of scheduled transfer is too long ({humanize_timedelta(self.requested_lifetime)}).\n"
            f"Maximum available lifetime is {humanize_timedelta(SCHEDULED_TRANSFER_MAX_LIFETIME)}."
        )
        super().__init__(message, errno.EPERM)


class CLIInvalidPasswordError(CLIPrettyError):
    """Raise when trying to unlock a profile with an incorrect password."""

    def __init__(self, profile_name: str) -> None:
        """
        Initialize the CLIInvalidPasswordError with a profile name.

        Args:
            profile_name: The name of the profile for which the password is incorrect.

        Returns:
            None
        """
        message = f"Password for profile `{profile_name}` is incorrect."
        super().__init__(message, errno.EPERM)


class CLIInvalidPasswordRepeatError(CLIPrettyError):
    """Raise when trying to create a profile with a repeated password that does not match the original."""

    def __init__(self) -> None:
        """
        Initialize the CLIInvalidPasswordRepeatError.

        Returns:
            None
        """
        message = (
            "Repeated password doesn't match previously entered password."
            " The profile was not created. Please try again."
        )
        super().__init__(message, errno.EPERM)


class CLISessionNotLockedError(CLIPrettyError):
    """Raise when trying to perform an action that requires all wallets in the session to be locked."""

    def __init__(self) -> None:
        """
        Initialize the CLISessionNotLockedError.

        Returns:
            None
        """
        message = "All wallets in session should be locked."
        super().__init__(message, errno.EPERM)


class CLIInvalidSelectionError(CLIPrettyError):
    """Raise when trying to perform an action with an invalid selection."""

    def __init__(self) -> None:
        """
        Initialize the CLIInvalidSelectionError.

        Returns:
            None
        """
        super().__init__("Invalid selection.", errno.EINVAL)


class CLIBeekeeperRemoteAddressIsNotSetError(CLIPrettyError):
    """Raise when trying to use CLI without a beekeeper remote address set."""

    MESSAGE: Final[str] = "Beekeeper remote address is not set. Please run via start_clive_cli.sh."

    def __init__(self) -> None:
        """
        Initialize the CLIBeekeeperRemoteAddressIsNotSetError.

        Returns:
            None
        """
        super().__init__(self.MESSAGE, errno.EINVAL)


class CLINoProfileUnlockedError(CLIPrettyError):
    """Raise when trying to perform an action that requires an unlocked profile, but no profile is unlocked."""

    MESSAGE: Final[str] = "There is no unlocked profile on the beekeeper. Perform `clive unlock` command first."

    def __init__(self) -> None:
        """
        Initialize the CLINoProfileUnlockedError.

        Returns:
            None
        """
        super().__init__(self.MESSAGE, errno.EACCES)


class CLICreatingProfileCommunicationError(CLIPrettyError):
    """Raise when trying to create a profile but communication with the beekeeper fails."""

    MESSAGE: Final[str] = (
        "Profile can't be created because communication with beekeeper failed.\n"
        "Maybe wallet with this name already exists."
    )

    def __init__(self) -> None:
        """
        Initialize the CLICreatingProfileCommunicationError.

        Returns:
            None
        """
        super().__init__(self.MESSAGE, errno.EEXIST)


class CLIBeekeeperRemoteAddressIsNotRespondingError(CLIPrettyError):
    """Raise when trying to use CLI with a beekeeper remote address that is not responding."""

    def __init__(self, url: HttpUrl) -> None:
        """
        Initialize the CLIBeekeeperRemoteAddressIsNotRespondingError with a URL.

        Args:
            url: The URL of the beekeeper remote address that is not responding.

        Returns:
            None
        """
        message = f"Beekeeper on address {url} is not responding."
        super().__init__(message, errno.EEXIST)


class CLIBeekeeperLocallyAlreadyRunningError(CLIPrettyError):
    """Raise when trying to spawn a new instance of Beekeeper while a local instance is already running."""

    def __init__(self, pid: int) -> None:
        """
        Initialize the CLIBeekeeperLocallyAlreadyRunningError with a process ID.

        Args:
            pid: The process ID of the already running local instance of Beekeeper.

        Returns:
            None
        """
        message = f"Local instance of Beekeeper is already running with pid {pid}"
        super().__init__(message, errno.EEXIST)


class CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError(CLIPrettyError):
    """Raise when trying to spawn a new instance of Beekeeper while environment variables are set."""

    def __init__(self) -> None:
        """
        Initialize the CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError.

        Returns:
            None
        """
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
        """
        Initialize the CLITransactionNotSignedError.

        Returns:
            None
        """
        super().__init__(self.MESSAGE, errno.EINVAL)


class CLITransactionUnknownAccountError(CLIPrettyError):
    """Raise when trying to perform transaction with operation(s) to unknown account."""

    def __init__(self, *account_names: str) -> None:
        """
        Initialize the CLITransactionUnknownAccountError with account names.

        Args:
            account_names: The names of the accounts that are not known.

        Returns:
            None
        """
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
        """
        Initialize the CLITransactionBadAccountError with account names.

        Args:
            account_names: The names of the accounts that are considered bad.

        Returns:
            None
        """
        self.account_names = list(account_names)

        message = (
            "Clive cannot perform the transaction because the "
            f"target accounts: {self.account_names} are on the list of bad accounts."
        )
        super().__init__(message, errno.EINVAL)


class CLITransactionToExchangeError(CLIPrettyError):
    """Raise when trying to perform transaction to exchange with operation(s) that cannot be performed."""

    def __init__(self, reason: str) -> None:
        """
        Initialize the CLITransactionToExchangeError with a reason.

        Args:
            reason: The reason why the transaction cannot be performed to the exchange.

        Returns:
            None
        """
        message = f"Cannot perform transaction.\n{reason}"
        super().__init__(message, errno.EINVAL)
        self.message = message
