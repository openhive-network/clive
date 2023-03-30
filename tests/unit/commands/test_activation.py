from __future__ import annotations

import pytest

import clive


def test_activate() -> None:
    # ARRANGE
    world = clive.World()

    # ACT
    world.commands.activate()

    # ASSERT
    assert world.app_state.is_active()


@pytest.mark.parametrize("is_default", [True, False], ids=["default", "after activation"])
def test_deactivate(is_default: bool) -> None:
    # ARRANGE
    world = clive.World()

    # ACT
    if not is_default:
        world.commands.activate()
        world.commands.deactivate()

    # ASSERT
    assert not world.app_state.is_active()
