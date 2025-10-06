from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.keys import PrivateKey
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

BRAIN_WALLET_PHRASE_WORDS_COUNT: Final[int] = 16


@pytest.mark.parametrize(
    "cli_tester_variant",
    [
        "unlocked",
        "locked",
        "without remote address",
        "without session token",
    ],
    indirect=True,
)
async def test_command_is_working_in_environment(cli_tester_variant: CLITester) -> None:
    # ACT & ASSERT
    cli_tester_variant.generate_secret_phrase()


async def test_generate_secret_phrase_length(cli_tester_locked: CLITester) -> None:
    """Check that clive generate secret-phrase command generates 16 worlds."""
    # ACT
    result = cli_tester_locked.generate_secret_phrase()

    # ASSERT
    words = result.stdout.strip().split()
    assert len(words) == BRAIN_WALLET_PHRASE_WORDS_COUNT, "Brain wallet phrase should have 16 words."


async def test_generate_secret_phrase_can_be_used_to_derive_keys(cli_tester_locked: CLITester) -> None:
    """Check that clive generate secret-phrase command can be input to command clive generate key-from-seed."""
    # ARRANGE
    result_secret_phrase = cli_tester_locked.generate_secret_phrase()
    seed = result_secret_phrase.stdout.strip()
    role = "active"

    # ACT
    result_key_from_seed = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=role, only_private_key=True, password_stdin=seed
    )

    # ASSERT
    PrivateKey.validate(result_key_from_seed.stdout.strip())
