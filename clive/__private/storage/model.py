from __future__ import annotations

from itertools import pairwise
from typing import get_type_hints

from clive.__private.storage.migrations.base import ProfileStorageBase
from clive.__private.storage.migrations.v2 import ProfileStorageModel

__all__ = ["ProfileStorageBase", "ProfileStorageModel"]


def apply_all_migrations(old_instance: ProfileStorageBase) -> ProfileStorageModel:
    new_instance = old_instance
    for model_cls in ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP.values():
        if new_instance.get_this_version_number() < model_cls.get_this_version_number():
            new_instance = model_cls.upgrade(new_instance)  # type: ignore[attr-defined]  # attribute existence validated at import time
    message = (
        f"After applying all migrations there should be last model of storage, actual model is {type(new_instance)}."
    )
    assert type(new_instance) is ProfileStorageModel, message
    return new_instance


def _validate_model_upgrades() -> None:
    for prev_hash, this_hash in pairwise(ProfileStorageBase.REVISIONS):
        prev_cls = ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP[prev_hash]
        this_cls = ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP[this_hash]
        assert hasattr(this_cls, "upgrade"), f"Upgrade function should be defined for {this_cls}, but it is not."
        hints = get_type_hints(this_cls.upgrade)
        assert hints["old"] is prev_cls, (
            f"Upgrade function should accept {prev_cls} as first argument, but it takes {hints['old']} instead."
        )
        assert hints["return"] is this_cls, (
            f"Upgrade function should return {this_cls}, but it returns {hints['return']} instead."
        )


def _validate_model_alias() -> None:
    assert ProfileStorageModel is ProfileStorageBase.get_current_model_cls(), (
        f"ProfileStorageModel should be alias to newest model, but it is {ProfileStorageModel} instead."
    )


_validate_model_upgrades()
_validate_model_alias()
