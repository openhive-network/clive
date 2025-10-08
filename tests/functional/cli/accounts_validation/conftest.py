from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import pytest

from clive_local_tools.helpers import create_transaction_filepath

if TYPE_CHECKING:
    from pathlib import Path


class ActionSelector(TypedDict):
    broadcast: bool
    save_file: Path | None


@pytest.fixture(params=["broadcast", "save_file", "show"])
def process_action_selector(request: pytest.FixtureRequest) -> ActionSelector:
    if request.param == "broadcast":
        return ActionSelector(broadcast=True, save_file=None)
    if request.param == "save_file":
        return ActionSelector(broadcast=False, save_file=create_transaction_filepath())
    if request.param == "show":
        return ActionSelector(broadcast=False, save_file=None)
    raise AssertionError(f"Unknown param: {request.param}")
