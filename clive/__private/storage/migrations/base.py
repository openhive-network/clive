from __future__ import annotations

from abc import ABC
from hashlib import sha256
from typing import Any, ClassVar

from clive.__private.models.base import CliveBaseModel


class ProfileStorageBase(CliveBaseModel, ABC):
    REVISIONS: ClassVar[list[str]] = []
    REVISION_TO_MODEL_TYPE_MAP: ClassVar[dict[str, type[ProfileStorageBase]]] = {}

    def __init_subclass__(cls: type[ProfileStorageBase], *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)
        revision = cls.calculate_storage_model_revision()
        ProfileStorageBase.REVISIONS.append(revision)
        ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP[revision] = cls

    def __hash__(self) -> int:
        return hash(self.json(indent=4))

    @classmethod
    def calculate_storage_model_revision(cls) -> str:
        assert cls is not ProfileStorageBase, "This method should be called on subclass."
        return sha256(cls.schema_json(indent=4).encode()).hexdigest()[:8]

    @staticmethod
    def get_current_model_cls() -> type[ProfileStorageBase]:
        return ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP[ProfileStorageBase.REVISIONS[-1]]

    @staticmethod
    def get_current_version_number() -> int:
        return len(ProfileStorageBase.REVISIONS) - 1

    @classmethod
    def get_this_version_number(cls) -> int:
        return ProfileStorageBase.REVISIONS.index(cls.calculate_storage_model_revision())

    @staticmethod
    def version_number_to_model_cls(num: int) -> type[ProfileStorageBase]:
        revision_hash = ProfileStorageBase.REVISIONS[num]
        return ProfileStorageBase.REVISION_TO_MODEL_TYPE_MAP[revision_hash]
