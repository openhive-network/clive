from __future__ import annotations

import clive


def test_transfer() -> None:
    # ARRANGE
    world = clive.World()

    # ACT
    command = world.commands.transfer(from_="initminer", to="alice", amount="1.000", asset="HIVE")
    command.execute()

    # ASSERT
    assert command.result is True
