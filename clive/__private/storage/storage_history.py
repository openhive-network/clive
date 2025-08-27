from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.storage.migrations.base import ProfileStorageBase

if TYPE_CHECKING:
    from clive.__private.storage.current_model import ProfileStorageModel  # noqa: TC004
    from clive.__private.storage.migrations.base import Revision, Version


class StorageHistory:
    _initialized: ClassVar[bool] = False

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return

        cls._get_current_profile_storage_model_cls_lazy()  # required before gather so all classes are registered
        ProfileStorageBase.gather()
        cls._validate_current_profile_storage_model_alias()
        cls._initialized = True

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
        current_storage_model_cls = cls._get_current_profile_storage_model_cls_lazy()
        assert type(new_instance) is current_storage_model_cls, message
        return new_instance

    @classmethod
    def _validate_current_profile_storage_model_alias(cls) -> None:
        latest_version = ProfileStorageBase._get_latest_version()
        latest_cls = ProfileStorageBase._get_model_cls_for_version(latest_version)
        current_storage_model_cls = cls._get_current_profile_storage_model_cls_lazy()
        assert current_storage_model_cls is latest_cls, (
            f"ProfileStorageModel should be alias to newest model, but it is {current_storage_model_cls} instead."
        )

    @staticmethod
    def _get_current_profile_storage_model_cls_lazy() -> type[ProfileStorageModel]:
        from clive.__private.storage.current_model import ProfileStorageModel  # noqa: PLC0415

        return ProfileStorageModel
