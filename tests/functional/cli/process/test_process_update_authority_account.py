from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_authority_weight, assert_is_authority, assert_is_not_authority
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.testing_cli import TestingCli


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]
WEIGHT: Final[int] = 123
MODIFIED_WEIGHT: Final[int] = 124


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_account(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-account")(account=OTHER_ACCOUNT.name, weight=WEIGHT)

    # ASSERT
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.name, authority, WEIGHT)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_remove_account(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-account")(account=OTHER_ACCOUNT.name, weight=WEIGHT)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)

    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "remove-account")(account=OTHER_ACCOUNT.name)

    # ASSERT
    assert_is_not_authority(testing_cli, OTHER_ACCOUNT.name, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_account(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-account")(account=OTHER_ACCOUNT.name, weight=WEIGHT)
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)

    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "modify-account")(account=OTHER_ACCOUNT.name, weight=MODIFIED_WEIGHT)

    # ASSERT
    assert_is_authority(testing_cli, OTHER_ACCOUNT.name, authority)
    assert_authority_weight(testing_cli, OTHER_ACCOUNT.name, authority, MODIFIED_WEIGHT)
