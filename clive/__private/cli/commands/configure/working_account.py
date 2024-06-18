import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import (
    CLIPrettyError,
    CLIWorkingAccountIsAlreadySetError,
    CLIWorkingAccountIsNotSetError,
)
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.account_name_validator import AccountNameValidator


@dataclass(kw_only=True)
class AddWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        if self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsAlreadySetError(self.profile_data)

        result = AccountNameValidator().validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.profile_data.set_working_account(self.account_name)


@dataclass(kw_only=True)
class RemoveWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account_name = self.account_name

        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        profile_working_account_name = self.profile_data.working_account.name

        if profile_working_account_name != account_name:
            raise CLIPrettyError(
                (
                    f"Given account name `{self.account_name}` is different than the one in the profile:"
                    f" `{profile_working_account_name}`"
                ),
                exit_code=errno.EINVAL,
            )

        self.profile_data.unset_working_account()
