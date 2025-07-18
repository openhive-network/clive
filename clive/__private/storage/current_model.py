from __future__ import annotations

from clive.__private.storage.migrations.base import ProfileStorageBase
from clive.__private.storage.migrations.v2 import ProfileStorageModel

__all__ = ["ProfileStorageModel"]


def _validate_current_model_alias() -> None:
    version = ProfileStorageBase._get_latest_version()
    cls = ProfileStorageBase._get_model_cls_for_version(version)
    assert ProfileStorageModel is cls, (
        f"ProfileStorageModel should be alias to newest model, but it is {ProfileStorageModel} instead."
    )


ProfileStorageBase.gather()
_validate_current_model_alias()
