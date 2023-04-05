from __future__ import annotations

import asyncio
from datetime import timedelta

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


@pytest.mark.asyncio
async def test_deactivate_after_given_time() -> None:
    # ARRANGE
    world = clive.World()

    # ACT
    world.commands.activate(active_mode_time=timedelta(seconds=0.01))
    await asyncio.sleep(0.02)

    # ASSERT
    assert not world.app_state.is_active()
