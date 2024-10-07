import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIPrettyError,
    CLIWorkingAccountIsAlreadySetError,
    CLIWorkingAccountIsNotSetError,
)
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator


@dataclass(kw_only=True)
class SetWorkingAccount(WorldBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        if self.world.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsAlreadySetError(self.world.profile)

        result = SetTrackedAccountValidator(self.world.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.world.profile.accounts.set_working_account(self.account_name)


@dataclass(kw_only=True)
class UnsetWorkingAccount(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account_name = self.account_name

        if not self.world.profile.accounts.has_working_account:
            raise CLIWorkingAccountIsNotSetError(self.world.profile)

        profile_working_account_name = self.world.profile.accounts.working.name

        if profile_working_account_name != account_name:
            raise CLIPrettyError(
                (
                    f"Given account name `{self.account_name}` is different than the one in the profile:"
                    f" `{profile_working_account_name}`"
                ),
                exit_code=errno.EINVAL,
            )

        self.world.profile.accounts.unset_working_account()
