from __future__ import annotations

from typing import Final

from clive.__private.storage.current_model import ProfileStorageModel
from clive.__private.storage.storage_history import StorageHistory

REVISIONS: Final[list[str]] = ["0313f118", "aaae09eb", "b52dcff7"]
LATEST_REVISION: Final[str] = REVISIONS[-1]


def test_storage_revision_doesnt_changed_for_latest_version() -> None:
    # ARRANGE
    info_message = (
        "Storage model revision has changed. If you are sure that it is expected, please update the expected revision."
    )

    # ACT
    actual_revision = ProfileStorageModel.get_this_revision()

    # ASSERT
    assert actual_revision == LATEST_REVISION, info_message


async def test_storage_revision_doesnt_changed_in_known_versions() -> None:
    # ARRANGE
    info_message = (
        "Revision hash in older storage versions shouldn't change, it means older storage"
        " versions may not be loaded properly, if you are sure this is expected check tests with"
        " loading of first profile revision including profile with transaction or alarms"
    )

    # ACT
    revisions = StorageHistory.get_revisions()

    # ASSERT
    assert revisions == REVISIONS, info_message
