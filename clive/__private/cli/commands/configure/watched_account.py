import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator


@dataclass(kw_only=True)
class AddWatchedAccount(WorldBasedCommand):
    account_name: str

    async def validate_inside_context_manager(self) -> None:
        result = SetTrackedAccountValidator(self.world.profile).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.world.profile.accounts.watched.add(self.account_name)


@dataclass(kw_only=True)
class RemoveWatchedAccount(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        self.world.profile.accounts.watched.remove(self.account_name)
