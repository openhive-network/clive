from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.cli.commands.show.show_pending_account_recovery import NO_PENDING_ACCOUNT_RECOVERY_MESSAGE
from clive.__private.core.keys.keys import PrivateKeyAliased, PublicKey
from clive_local_tools.testnet_block_log.constants import CREATOR_ACCOUNT, WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester


INITMINER_KEY_ALIAS = "initminer_key"
NEW_OWNER_KEY = PublicKey(value=WATCHED_ACCOUNTS_DATA[0].account.public_key)


async def _import_initminer_key(world: World) -> None:
    world.profile.keys.add_to_import(PrivateKeyAliased(value=CREATOR_ACCOUNT.private_key, alias=INITMINER_KEY_ALIAS))
    await world.commands.sync_data_with_beekeeper()
    await world.commands.save_profile()


async def test_show_pending_account_recovery_none(cli_tester: CLITester) -> None:
    """When no recovery request exists, should display appropriate message."""
    # ACT
    result = cli_tester.show_pending_account_recovery(account_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    assert NO_PENDING_ACCOUNT_RECOVERY_MESSAGE in result.stdout


async def test_show_pending_account_recovery(
    cli_tester: CLITester,
) -> None:
    """After requesting recovery, show pending account-recovery should display the request."""
    # ARRANGE
    await _import_initminer_key(cli_tester.world)

    cli_tester.process_request_account_recovery(
        recovery_account=CREATOR_ACCOUNT.name,
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_key=NEW_OWNER_KEY.value,
        sign_with=INITMINER_KEY_ALIAS,
    )

    # ACT
    result = cli_tester.show_pending_account_recovery(account_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    assert WORKING_ACCOUNT_NAME in result.output
    assert "Expires" in result.output
