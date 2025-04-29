from __future__ import annotations

from abc import ABC
from hashlib import sha256
from typing import Any, ClassVar, Self, get_type_hints

from clive.__private.models.base import CliveBaseModel
from clive.exceptions import CliveError

type Revision = str
type Version = int


class StorageRevisionNotFoundError(CliveError):
    def __init__(self, revision: Revision) -> None:
        self.message = f"Revision: {revision} not found. Available ones are: {ProfileStorageBase._get_revisions()}"
        super().__init__(self.message)


class StorageVersionNotFoundError(CliveError):
    def __init__(self, version: Version) -> None:
        self.message = f"Version: {version} not found. Available ones are: {ProfileStorageBase._get_versions()}"
        super().__init__(self.message)


class ProfileStorageBase(CliveBaseModel, ABC):
    _REVISIONS: ClassVar[list[Revision]] = []
    _REVISION_TO_MODEL_TYPE_MAP: ClassVar[dict[Revision, type[ProfileStorageBase]]] = {}

    _REVISION_NONCE: ClassVar[int] = 0

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)
        revision = cls.get_this_revision()
        assert revision not in cls._get_revisions(), f"Revision: {revision} already exists."
        cls._REVISIONS.append(revision)
        cls._REVISION_TO_MODEL_TYPE_MAP[revision] = cls
        cls._validate_upgrade_definition()

    def __hash__(self) -> int:
        return hash(self.json(indent=4))

    @classmethod
    def upgrade(cls, old: ProfileStorageBase) -> Self:
        raise NotImplementedError

    @classmethod
    def get_this_revision(cls) -> Revision:
        assert cls is not ProfileStorageBase, "This method should be called on subclass."
        return sha256(cls._get_revision_seed().encode()).hexdigest()[:8]

    @classmethod
    def get_this_version(cls) -> Version:
        return cls._get_revisions().index(cls.get_this_revision())

    @classmethod
    def _get_revisions(cls) -> list[Revision]:
        return cls._REVISIONS

    @classmethod
    def _get_latest_revision(cls) -> Revision:
        return cls._get_revisions()[-1]

    @classmethod
    def _get_versions(cls) -> list[Version]:
        return list(range(len(cls._get_revisions())))

    @classmethod
    def _get_latest_version(cls) -> Version:
        return cls._get_versions()[-1]

    @classmethod
    def _get_model_cls_for_revision(cls, revision: Revision) -> type[ProfileStorageBase]:
        try:
            return cls._REVISION_TO_MODEL_TYPE_MAP[revision]
        except KeyError as error:
            raise StorageRevisionNotFoundError(revision) from error

    @classmethod
    def _get_model_cls_for_version(cls, num: Version) -> type[ProfileStorageBase]:
        return cls._get_model_cls_for_revision(cls._get_revision_for_version(num))

    @classmethod
    def _get_all_model_cls(cls) -> list[type[ProfileStorageBase]]:
        return list(cls._REVISION_TO_MODEL_TYPE_MAP.values())

    @classmethod
    def _get_revision_for_version(cls, num: Version) -> Revision:
        try:
            return cls._get_revisions()[num]
        except IndexError as error:
            raise StorageVersionNotFoundError(num) from error

    @classmethod
    def _get_revision_seed(cls) -> str:
        return cls.schema_json(indent=4) + str(cls._REVISION_NONCE)

    @classmethod
    def _validate_upgrade_definition(cls) -> None:
        hints = get_type_hints(cls.upgrade)

        this_version = cls.get_this_version()
        prev_version = cls.get_this_version() - 1
        if this_version > 0:
            assert "old" in hints, f"Upgrade function of {cls} should accept 'old' parameter, but it doesn't."

            old_param = hints.get("old")
            prev_cls = cls._get_model_cls_for_version(prev_version)
            assert old_param is prev_cls, (
                f"Upgrade function of {cls} should accept {prev_cls}, but it takes {old_param} instead."
            )

            return_param = hints.get("return")
            assert return_param is Self, (
                f"Upgrade function of {cls} should return {Self}, but it returns {return_param} instead."
            )
