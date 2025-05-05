from __future__ import annotations

from typing import Final

from clive.__private.storage import ProfileStorageModel
from clive.__private.storage.storage_history import StorageHistory

REVISIONS: Final[list[str]] = ["ffc97b51", "a721f943", "9c46df0c"]
LATEST_REVISION: Final[str] = REVISIONS[-1]


def test_storage_revision_doesnt_changed_for_latest_version() -> None:
    # ACT
    actual_revision = ProfileStorageModel.get_this_revision()

    # ASSERT
    message = (
        "Storage model revision has changed. If you are sure that it is expected, please update the expected revision."
    )
    assert actual_revision == LATEST_REVISION, message


async def test_storage_revision_doesnt_changed_in_known_versions() -> None:
    # ARRANGE
    info_message = (
        "Revision hash in older storage versions shouldn't change, it means older storage"
        " versions may not be loaded properly, if you are sure this is expected check tests with"
        " loading of first profile revision including profile with transaction or alarms"
    )

    # ACT
    assert StorageHistory.get_revisions() == REVISIONS, info_message
