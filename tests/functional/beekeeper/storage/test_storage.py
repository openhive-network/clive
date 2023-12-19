from __future__ import annotations

import json
from pathlib import Path

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools import checkers


async def test_multiply_beekeepeer_same_storage(tmp_path: Path) -> None:
    """Test test_multiply_beekeepeer_same_storage will check, if it is possible to run multiple instances of beekeepers pointing to the same storage."""
    # ARRANGE
    same_storage = tmp_path / "same_storage"
    same_storage.mkdir()

    # ACT & ASSERT 1
    bk1 = await Beekeeper().launch(wallet_dir=same_storage)
    assert bk1.is_running is True, "First instance of beekeeper should launch without any problems."

    # ACT & ASSERT 2
    bk2 = Beekeeper()
    # Now we get assert because of https://gitlab.syncad.com/hive/hive/-/issues/622
    # Related clive:
    #   https://gitlab.syncad.com/hive/clive/-/issues/102
    # ACT & ASSERT
    with pytest.raises(AssertionError, match="Beekeeper webserver HTTP endpoint is not known yet"):
        await bk2.launch(wallet_dir=same_storage)
    assert bk2.is_running is False, "Second instance of beekeeper should exit with error."

    assert checkers.check_for_pattern_in_file(
        bk2.get_wallet_dir() / "stderr.log",
        "Failed to lock access to wallet directory; is another `beekeeper` running?",
    ), "There should be an info about another instance of beekeeper locking wallet directory."


async def test_multiply_beekeepeer_different_storage(tmp_path: Path) -> None:
    """Test test_multiply_beekeepeer_different_storage will check, if it is possible to run multiple instances of beekeepers pointing to the different storage."""
    # ARRANGE
    bk1_path = tmp_path / "bk1"
    bk1_path.mkdir()

    bk2_path = tmp_path / "bk2"
    bk2_path.mkdir()

    # ACT
    bk1 = await Beekeeper().launch(wallet_dir=bk1_path)
    bk2 = await Beekeeper().launch(wallet_dir=bk2_path)

    # ASSERT
    assert bk1.is_running, "First instance of beekeeper should be working."
    assert bk2.is_running, "Second instance of beekeeper should be working."

    await bk1.close()
    await bk2.close()

    for bk in [bk1, bk2]:
        assert (
            checkers.check_for_pattern_in_file(
                bk.get_wallet_dir() / "stderr.log",
                "Failed to lock access to wallet directory; is another `beekeeper` running?",
            )
            is False
        ), "There should be an no info about another instance of beekeeper locking wallet directory."


async def test_beekeepers_files_generation() -> None:
    """Test test_beekeepers_files_generation will check if beekeeper files are generated and how same content."""
    # ARRANGE & ACT
    async with Beekeeper() as bk:
        beekeeper_connection_file = bk.get_wallet_dir() / "beekeeper.connection"
        beekeeper_pid_file = bk.get_wallet_dir() / "beekeeper.pid"
        beekeeper_wallet_lock_file = bk.get_wallet_dir() / "beekeeper.wallet.lock"

        # ASSERT
        assert beekeeper_connection_file.exists() is True, "File 'beekeeper.connection' should exists"
        assert beekeeper_pid_file.exists() is True, "File 'beekeeper.pid' should exists"
        # File beekeeper.wallet.lock holds no value inside, so we need only to check is its exists.
        assert beekeeper_wallet_lock_file.exists() is True, "File 'beekeeper.wallet.lock' should exists"

        with Path.open(beekeeper_connection_file) as connection:
            content = json.load(connection)
            # because of notifications.py:87
            if bk.http_endpoint.host == "127.0.0.1":
                assert content["address"] in [
                    "0.0.0.0",
                    "127.0.0.1",
                ], "Address should point to localhost or all interfaces."
            else:
                assert content["address"] == bk.http_endpoint.host, "Host should be the same."
            assert content["port"] == bk.http_endpoint.port, "Port should be the same."
            assert content["type"].lower() == bk.http_endpoint.proto.lower(), "Protocol should be the same."

        with Path.open(beekeeper_pid_file) as pid:
            content = json.load(pid)

            assert content["pid"] == str(bk.pid), "Pid should be the same"
