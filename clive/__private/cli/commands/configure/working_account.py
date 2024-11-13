import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import (
    CLIPrettyError,
    CLIWorkingAccountIsAlreadySetError,
    CLIWorkingAccountIsNotSetError,
)
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator


@dataclass(kw_only=True)
class SetWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        if self.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsAlreadySetError(self.profile)

        result = SetTrackedAccountValidator(self.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.profile.accounts.set_working_account(self.account_name)


@dataclass(kw_only=True)
class UnsetWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account_name = self.account_name

        if not self.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsNotSetError(self.profile)

        profile_working_account_name = self.profile.accounts.working.name

        if profile_working_account_name != account_name:
            raise CLIPrettyError(
                (
                    f"Given account name `{self.account_name}` is different than the one in the profile:"
                    f" `{profile_working_account_name}`"
                ),
                exit_code=errno.EINVAL,
            )

        self.profile.accounts.unset_working_account()

@dataclass(kw_only=True)
class SwitchWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def _run(self) -> None:
        self.profile.accounts.switch_working_account(self.account_name)

    def _validate_already_working_account(self) -> None:
        if self.profile.accounts.is_account_working(self.account_name):
            raise CLIPrettyError(f"Account {self.account_name} is already a working account.") from None

    async def validate_inside_context_manager(self) -> None:
        self._validate_account_exists(self.account_name)
        self._validate_already_working_account()
        await super().validate_inside_context_manager()
