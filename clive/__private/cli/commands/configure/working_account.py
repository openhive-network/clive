import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import (
    CLIPrettyError,
    CLIWorkingAccountIsAlreadySetError,
    CLIWorkingAccountIsNotSetError,
)


@dataclass(kw_only=True)
class AddWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def _run(self) -> None:
        if self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsAlreadySetError(self.profile_data)

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
