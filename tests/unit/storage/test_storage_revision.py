from __future__ import annotations

from typing import Final

from clive.__private.storage.current_model import ProfileStorageModel
from clive.__private.storage.storage_history import StorageHistory

REVISIONS: Final[list[str]] = ["d892ab66", "9a37ce27", "7b6245aa", "014d8b80"]
LATEST_REVISION: Final[str] = REVISIONS[-1]
SCHEMA_REVISIONS: Final[list[str]] = ["8395171c", "9a37ce27", "7b6245aa", "014d8b80"]
"""Revisions computed from schemas of models of the versions - differ from `REVISIONS` only for frozen revisions."""


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


def test_storage_schema_revision_doesnt_changed_in_known_versions() -> None:
    # ARRANGE
    info_message = (
        "Schema of a storage model has changed (also of a model it embeds, e.g. from a library). Stored profiles of"
        " known versions may not be loaded properly - add a new storage version instead of changing the existing ones."
    )
    StorageHistory.initialize()

    # ACT
    schema_revisions = [model_cls.get_schema_revision() for model_cls in StorageHistory.get_all_model_cls()]

    # ASSERT
    assert schema_revisions == SCHEMA_REVISIONS, info_message
