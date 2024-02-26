from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_authority_weight, assert_is_authority, assert_is_not_authority
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


other_account = WATCHED_ACCOUNTS[0]
weight = 123
modified_weight = 124


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)

    # ASSERT
    assert_is_authority(testing_cli, other_account.public_key, authority)
    assert_authority_weight(testing_cli, other_account.public_key, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_remove_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)
    assert_is_authority(testing_cli, other_account.public_key, authority)

    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "remove-key")(key=other_account.public_key)

    # ASSERT
    assert_is_not_authority(testing_cli, other_account.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)
    assert_is_authority(testing_cli, other_account.public_key, authority)

    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "modify-key")(key=other_account.public_key, weight=modified_weight)

    # ASSERT
    assert_is_authority(testing_cli, other_account.public_key, authority)
    assert_authority_weight(testing_cli, other_account.public_key, authority, modified_weight)
