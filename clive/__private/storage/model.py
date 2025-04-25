from __future__ import annotations

from itertools import pairwise
from typing import Self, get_type_hints

from clive.__private.storage.migrations.base import ProfileStorageBase
from clive.__private.storage.migrations.v2 import ProfileStorageModel

__all__ = ["ProfileStorageBase", "ProfileStorageModel"]


def apply_all_migrations(old_instance: ProfileStorageBase) -> ProfileStorageModel:
    new_instance = old_instance
    for model_cls in ProfileStorageBase._REVISION_TO_MODEL_TYPE_MAP.values():
        if new_instance.get_this_version() < model_cls.get_this_version():
            new_instance = model_cls.upgrade(new_instance)  # type: ignore[attr-defined]  # attribute existence validated at import time
    message = (
        f"After applying all migrations there should be last model of storage, actual model is {type(new_instance)}."
    )
    assert type(new_instance) is ProfileStorageModel, message
    return new_instance


def _validate_model_upgrades() -> None:
    for prev_hash, this_hash in pairwise(ProfileStorageBase.get_revisions()):
        prev_cls = ProfileStorageBase.get_model_cls_for_revision(prev_hash)
        this_cls = ProfileStorageBase.get_model_cls_for_revision(this_hash)

        assert hasattr(this_cls, "upgrade"), f"Upgrade function should be defined for {this_cls}, but it is not."

        hints = get_type_hints(this_cls.upgrade)
        old_param = hints.get("old")
        return_param = hints.get("return")

        assert old_param is prev_cls, (
            f"Upgrade function of {this_cls} should accept {prev_cls}, but it takes {old_param} instead."
        )
        assert return_param is Self, (
            f"Upgrade function of {this_cls} should return {Self}, but it returns {return_param} instead."
        )


def _validate_model_alias() -> None:
    assert ProfileStorageModel is ProfileStorageBase.get_model_cls_for_revision(
        ProfileStorageBase.get_latest_revision()
    ), f"ProfileStorageModel should be alias to newest model, but it is {ProfileStorageModel} instead."


_validate_model_upgrades()
_validate_model_alias()
