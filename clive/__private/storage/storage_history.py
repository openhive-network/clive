from __future__ import annotations

from itertools import pairwise
from typing import Self, get_type_hints

from clive.__private.storage.current_model import ProfileStorageModel
from clive.__private.storage.migrations.base import ProfileStorageBase, Revision, Version


class StorageHistory:
    @staticmethod
    def get_revisions() -> list[Revision]:
        return ProfileStorageBase._get_revisions()

    @staticmethod
    def get_latest_revision() -> Revision:
        return ProfileStorageBase._get_latest_revision()

    @staticmethod
    def get_versions() -> list[Version]:
        return ProfileStorageBase._get_versions()

    @staticmethod
    def get_latest_version() -> Version:
        return ProfileStorageBase._get_latest_version()

    @staticmethod
    def get_model_cls_for_revision(revision: Revision) -> type[ProfileStorageBase]:
        return ProfileStorageBase._get_model_cls_for_revision(revision)

    @staticmethod
    def get_latest_model_cls() -> type[ProfileStorageModel]:
        return ProfileStorageModel

    @staticmethod
    def get_all_model_cls() -> list[type[ProfileStorageBase]]:
        return ProfileStorageBase._get_all_model_cls()

    @staticmethod
    def get_model_cls_for_version(version: Version) -> type[ProfileStorageBase]:
        return ProfileStorageBase._get_model_cls_for_version(version)

    @classmethod
    def apply_all_migrations(cls, old_instance: ProfileStorageBase) -> ProfileStorageModel:
        new_instance = old_instance
        for model_cls in cls.get_all_model_cls():
            if new_instance.get_this_version() < model_cls.get_this_version():
                new_instance = model_cls.upgrade(new_instance)
        message = (
            f"After applying all migrations there should be last model of storage,"
            f" actual model is {type(new_instance)}."
        )
        assert type(new_instance) is ProfileStorageModel, message
        return new_instance

    @classmethod
    def _validate_model_upgrades(cls) -> None:
        for prev_hash, this_hash in pairwise(cls.get_revisions()):
            prev_cls = cls.get_model_cls_for_revision(prev_hash)
            this_cls = cls.get_model_cls_for_revision(this_hash)

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


StorageHistory._validate_model_upgrades()
