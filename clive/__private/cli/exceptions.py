from __future__ import annotations

import errno
from typing import TYPE_CHECKING

from click import ClickException

if TYPE_CHECKING:
    from typing import TypeAlias

    from clive.__private.core.profile_data import ProfileData
    from clive.models import Asset


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
    def __init__(self, profile: ProfileData | None = None) -> None:
        self.profile = profile
        message = (
            f"Working account is not set{f' for the `{profile.name}` profile' if profile else ''}.\n"
            "Please check the `clive configure working-account add -h` command first."
        )
        super().__init__(message, errno.ENOENT)


class CLIWorkingAccountIsAlreadySetError(CLIPrettyError):
    def __init__(self, profile: ProfileData | None = None) -> None:
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


class CLISigningRequiresAPasswordError(CLIPrettyError):
    def __init__(self) -> None:
        message = "You must provide a password to sign the transaction with."
        super().__init__(message, errno.EINVAL)


class CLIBroadcastRequiresSignKeyAndPasswordError(CLIPrettyError):
    def __init__(self) -> None:
        message = (
            "You must provide a password and a key alias to sign the transaction with if you want to broadcast it."
        )
        super().__init__(message, errno.EINVAL)


class CLIBroadcastCannotBeUsedWithForceUnsignError(CLIPrettyError):
    def __init__(self) -> None:
        message = "You cannot broadcast a transaction and force-unsign it at the same time."
        super().__init__(message, errno.EINVAL)


class InvalidAssetError(CLIPrettyError):
    def __init__(self, asset: Asset.AnyT, expected_type: TypeAlias) -> None:
        message = f"Asset format is invalid. Actual asset is {asset.as_legacy()}, expected instance of {expected_type}"
        super().__init__(message, errno.EINVAL)


class PowerDownInProgressError(CLIPrettyError):
    def __init__(self) -> None:
        message = "Power-down is already in progress, if you want to discard existing power-down and create new then use command `clive process power-down restart`"
        super().__init__(message, errno.EPERM)
