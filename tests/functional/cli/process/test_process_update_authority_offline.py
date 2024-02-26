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


weight_threshold = 12
other_account = WATCHED_ACCOUNTS[0]
weight = 323
modified_weight = 324


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold_offline(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            "--force-offline", password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
        )
        getattr(chain_command_builder, "add-account")(account=WORKING_ACCOUNT.name, weight=weight)

    # ASSERT
    assert_weight_threshold(testing_cli, authority, weight_threshold)
    assert_is_authority(testing_cli, WORKING_ACCOUNT.name, authority)
    assert_authority_weight(testing_cli, WORKING_ACCOUNT.name, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_account_offline(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            "--force-offline", password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-account")(account=other_account.name, weight=weight)

    # ASSERT
    assert_is_authority(testing_cli, other_account.name, authority)
    assert_authority_weight(testing_cli, other_account.name, authority, weight)
    assert_is_not_authority(testing_cli, WORKING_ACCOUNT.name, authority)
    assert_is_not_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key_offline(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    with testing_cli.chain_commands() as chain_command_builder:
        getattr(chain_command_builder, f"process_update-{authority}-authority")(
            "--force-offline", password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS
        )
        getattr(chain_command_builder, "add-key")(key=WORKING_ACCOUNT.public_key, weight=weight)
        getattr(chain_command_builder, "modify-key")(key=WORKING_ACCOUNT.public_key, weight=modified_weight)

    # ASSERT
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
    assert_authority_weight(testing_cli, WORKING_ACCOUNT.public_key, authority, modified_weight)
