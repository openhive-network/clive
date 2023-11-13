from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIWorkingAccountIsAlreadySetError, CLIWorkingAccountIsNotSetError


@dataclass(kw_only=True)
class AddWorkingAccount(ProfileBasedCommand):
    account_name: str

    async def run(self) -> None:
        if self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsAlreadySetError(self.profile_data)

        self.profile_data.set_working_account(self.account_name)


@dataclass(kw_only=True)
class RemoveWorkingAccount(ProfileBasedCommand):
    async def run(self) -> None:
        if not self.profile_data.is_working_account_set():
            raise CLIWorkingAccountIsNotSetError(self.profile_data)

        self.profile_data.unset_working_account()
