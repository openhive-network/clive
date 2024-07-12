import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.storage.accounts import Account
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator


@dataclass(kw_only=True)
class AddWatchedAccount(ProfileBasedCommand):
    account_name: str

    async def validate(self) -> None:
        result = SetTrackedAccountValidator(self.profile_data).validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {humanize_validation_result(result)}", errno.EINVAL)

    async def _run(self) -> None:
        self.profile_data.watched_accounts.add(Account(self.account_name))


@dataclass(kw_only=True)
class RemoveWatchedAccount(ProfileBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account = next(
            (account for account in self.profile_data.watched_accounts if account.name == self.account_name), None
        )
        if account is not None:
            self.profile_data.watched_accounts.discard(account)
