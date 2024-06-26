import errno
from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.storage.accounts import Account
from clive.__private.validators.account_name_validator import AccountNameValidator


@dataclass(kw_only=True)
class AddWatchedAccount(ProfileBasedCommand):
    account_name: str

    async def validate(self) -> None:
        result = AccountNameValidator().validate(self.account_name)
        if not result.is_valid:
            raise CLIPrettyError(f"Can't use this account name: {result.failure_descriptions}", errno.EINVAL)

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
