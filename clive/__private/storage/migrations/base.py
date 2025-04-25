from __future__ import annotations

from abc import ABC
from hashlib import sha256
from typing import Any, ClassVar

from clive.__private.models.base import CliveBaseModel
from clive.exceptions import CliveError

type Revision = str
type Version = int


class StorageRevisionNotFoundError(CliveError):
    def __init__(self, revision: Revision) -> None:
        self.message = f"Revision: {revision} not found. Available ones are: {ProfileStorageBase.get_revisions()}"
        super().__init__(self.message)


class StorageVersionNotFoundError(CliveError):
    def __init__(self, version: Version) -> None:
        self.message = f"Version: {version} not found. Available ones are: {ProfileStorageBase.get_versions()}"
        super().__init__(self.message)


class ProfileStorageBase(CliveBaseModel, ABC):
    _REVISIONS: ClassVar[list[Revision]] = []
    _REVISION_TO_MODEL_TYPE_MAP: ClassVar[dict[Revision, type[ProfileStorageBase]]] = {}

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)
        revision = cls.get_this_revision()
        cls._REVISIONS.append(revision)
        cls._REVISION_TO_MODEL_TYPE_MAP[revision] = cls

    def __hash__(self) -> int:
        return hash(self.json(indent=4))

    @classmethod
    def get_revisions(cls) -> list[Revision]:
        return cls._REVISIONS

    @classmethod
    def get_latest_revision(cls) -> Revision:
        return cls.get_revisions()[-1]

    @classmethod
    def get_versions(cls) -> list[Version]:
        return list(range(len(cls.get_revisions())))

    @classmethod
    def get_latest_version(cls) -> Version:
        return cls.get_versions()[-1]

    @classmethod
    def get_this_revision(cls) -> Revision:
        assert cls is not ProfileStorageBase, "This method should be called on subclass."
        return sha256(cls.schema_json(indent=4).encode()).hexdigest()[:8]

    @classmethod
    def get_this_version(cls) -> Version:
        return cls.get_revisions().index(cls.get_this_revision())

    @classmethod
    def get_model_cls_for_revision(cls, revision: Revision) -> type[ProfileStorageBase]:
        try:
            return cls._REVISION_TO_MODEL_TYPE_MAP[revision]
        except KeyError as error:
            raise StorageRevisionNotFoundError(revision) from error

    @classmethod
    def get_model_cls_for_version(cls, num: Version) -> type[ProfileStorageBase]:
        return cls.get_model_cls_for_revision(cls._get_revision_for_version(num))

    @classmethod
    def _get_revision_for_version(cls, num: Version) -> Revision:
        try:
            return cls.get_revisions()[num]
        except IndexError as error:
            raise StorageVersionNotFoundError(num) from error
