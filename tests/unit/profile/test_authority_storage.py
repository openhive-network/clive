from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.profile import Profile
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_NAME,
    ALT_WORKING_ACCOUNT2_NAME,
    ALT_WORKING_ACCOUNT3_NAME,
    WATCHED_ACCOUNTS_NAMES,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.world import World


async def test_if_authorities_are_saved(world: World, wallet_name: str, prepared_block_log_node: tt.RawNode) -> None:  # noqa: ARG001
    # ARRANGE
    world.profile.accounts.set_working_account(ALT_WORKING_ACCOUNT3_NAME)
    expected_posting_lut_names = [
        ALT_WORKING_ACCOUNT1_NAME,
        ALT_WORKING_ACCOUNT2_NAME,
        ALT_WORKING_ACCOUNT3_NAME,
        WATCHED_ACCOUNTS_NAMES[0],
    ]

    # ACT
    (await world.commands.update_authority_data(account=world.profile.accounts.working)).raise_if_error_occurred()
    world.profile.save()

    # ASSERT
    loaded_profile = Profile.load(wallet_name)
    loaded_authorities = loaded_profile.accounts.working.authorities
    assert loaded_authorities, "no authorities loaded"
    for name in expected_posting_lut_names:
        assert name in loaded_authorities.posting_lut, f"{name} not in posting lut"
