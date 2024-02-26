from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_weight_threshold,
)
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


other_account = WATCHED_ACCOUNTS[0]
other_account2 = WATCHED_ACCOUNTS[1]
weight = 213
modified_weight = 214
weight_threshold = 2


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
        )
        getattr(chain_command_builder, "add-account")(account=other_account.name, weight=weight)
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)

    # ASSERT
    assert_weight_threshold(testing_cli, authority, weight_threshold)
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(testing_cli, other_account.name, authority)
    assert_is_authority(testing_cli, other_account.public_key, authority)
    assert_authority_weight(testing_cli, other_account.name, authority, weight)
    assert_authority_weight(testing_cli, other_account.public_key, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining2(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
        )
        getattr(chain_command_builder, "add-account")(account=other_account.name, weight=weight)
        getattr(chain_command_builder, "add-account")(account=other_account2.name, weight=weight)
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)
        getattr(chain_command_builder, "remove-key")(key=WORKING_ACCOUNT.public_key)

    # ASSERT
    assert_weight_threshold(testing_cli, authority, weight_threshold)
    assert_is_authority(testing_cli, other_account.name, authority)
    assert_is_authority(testing_cli, other_account2.name, authority)
    assert_is_authority(testing_cli, other_account.public_key, authority)
    assert_authority_weight(testing_cli, other_account2.name, authority, weight)
    assert_authority_weight(testing_cli, other_account.public_key, authority, weight)
    assert_is_not_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_chaining3(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
        )
        getattr(chain_command_builder, "add-key")(key=other_account.public_key, weight=weight)
        getattr(chain_command_builder, "add-account")(account=other_account.name, weight=weight)
        getattr(chain_command_builder, "modify-key")(key=WORKING_ACCOUNT.public_key, weight=modified_weight)

    # ASSERT
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
    assert_is_authority(testing_cli, other_account.public_key, authority)
    assert_is_authority(testing_cli, other_account.name, authority)
    assert_authority_weight(testing_cli, WORKING_ACCOUNT.public_key, authority, modified_weight)
    assert_authority_weight(testing_cli, other_account.public_key, authority, weight)
    assert_authority_weight(testing_cli, other_account.name, authority, weight)
