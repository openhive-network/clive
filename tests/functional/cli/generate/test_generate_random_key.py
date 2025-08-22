from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.keys import PrivateKey, PublicKey

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_default_key_pairs(cli_tester_locked: CLITester) -> None:
    """Check clive generate random-key command."""
    # ACT
    result = cli_tester_locked.generate_random_key()

    # ASSERT
    private_key = PrivateKey(value=result.stdout.strip().split()[0])
    public_key = PublicKey(value=result.stdout.strip().split()[1])
    assert private_key.calculate_public_key() == public_key, "Public key should match private key."


async def test_custom_key_pairs(cli_tester_locked: CLITester) -> None:
    """Check clive generate random-key command with not default `--key-pairs` argument."""
    # ARRANGE
    key_pairs = 5

    # ACT
    result = cli_tester_locked.generate_random_key(key_pairs=key_pairs)

    # ASSERT
    lines = result.stdout.strip().split("\n")
    assert len(lines) == 2 * key_pairs, f"There should be {key_pairs} key pairs in output."
