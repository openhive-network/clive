from __future__ import annotations

from typing import TYPE_CHECKING

import clive

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def test_transfer(capsys: CaptureFixture[str]) -> None:
    # ARRANGE
    world = clive.World()
    expected_message = "Operation sent"

    # ACT
    world.commands.transfer(from_="initminer", to="alice", amount="1.000", asset="HIVE").execute()

    # ASSERT
    out, err = capsys.readouterr()
    assert expected_message in out
