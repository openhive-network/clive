from dataclasses import dataclass

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.storage.accounts import Account


@dataclass(kw_only=True)
class AddWatchedAccount(ProfileBasedCommand):
    account_name: str

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
