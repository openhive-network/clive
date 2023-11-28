from dataclasses import dataclass

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.profile_data import ProfileData
from clive.exceptions import CommunicationError


@dataclass(kw_only=True)
class CreateProfile(BeekeeperBasedCommand):
    profile_name: str
    password: str
    working_account_name: str | None = None

    async def _run(self) -> None:
        profile = ProfileData(self.profile_name, self.working_account_name)

        profile.save()

        try:
            await CreateWallet(beekeeper=self.beekeeper, wallet=profile.name, password=self.password).execute()
        except CommunicationError:
            profile.delete()
            raise


@dataclass(kw_only=True)
class DeleteProfile(ExternalCLICommand):
    profile_name: str

    async def run(self) -> None:
        ProfileData.delete_by_name(self.profile_name)


@dataclass(kw_only=True)
class SetDefaultProfile(ExternalCLICommand):
    profile_name: str

    async def run(self) -> None:
        ProfileData.set_default_profile(self.profile_name)
