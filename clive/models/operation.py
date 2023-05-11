from __future__ import annotations

import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import inflection
from pydantic import BaseModel

from clive.__private.abstract_class import AbstractClass

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


class Operation(BaseModel, AbstractClass):
    def as_json(self, indent: int = 4) -> str:
        return json.dumps(self.dict(by_alias=True), indent=indent)

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the operation."""

    @abstractmethod
    def pretty(self, *, separator: str = "\n") -> str:
        """This method should return short, formatted description of operation without op type"""

    def json(
        self,
        *,
        include: AbstractSetIntStr | MappingIntStrAny | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
        by_alias: bool = False,
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Callable[[Any], Any] | None = None,
        models_as_dict: bool = True,
        **kwargs: Any,
    ) -> str:
        value = super().json(by_alias=by_alias, **kwargs)
        data = {
            "type": inflection.underscore(self.__class__.__name__),
            "value": json.loads(value)
        }

        return json.dumps(data)
