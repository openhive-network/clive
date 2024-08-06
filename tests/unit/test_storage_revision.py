from __future__ import annotations

from typing import Final

from clive.__private.storage.model import calculate_storage_model_revision


def test_storage_revision_doesnt_changed() -> None:
    # ARRANGE
    expected_revision: Final[str] = "2c0d6f2e"

    # ACT
    actual_revision = calculate_storage_model_revision()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected,"
        " please update the expected revision."
    )
    assert actual_revision == expected_revision, message
