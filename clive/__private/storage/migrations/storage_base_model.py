from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel

from clive.__private.core.constants.date import TIME_FORMAT_WITH_SECONDS
from clive.__private.models.schemas import Serializable

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class StorageBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_encoders = {  # noqa: RUF012; pydantic convention
            datetime: lambda d: d.strftime(TIME_FORMAT_WITH_SECONDS),
            Serializable: lambda x: x.serialize(),
        }

    def json(  # noqa: PLR0913
        self,
        *,
        include: AbstractSetIntStr | MappingIntStrAny | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
        by_alias: bool = True,  # modified, most of the time we want to dump by alias
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Callable[[Any], Any] | None = None,
        models_as_dict: bool = True,
        ensure_ascii: bool = False,  # modified, so unicode characters are not escaped, will properly dump e.g. polish characters # noqa: E501
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            ensure_ascii=ensure_ascii,
            **dumps_kwargs,
        )

    def dict(  # noqa: PLR0913
        self,
        *,
        include: AbstractSetIntStr | MappingIntStrAny | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
        by_alias: bool = True,  # modified, most of the time we want to dump by alias
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> DictStrAny:
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
