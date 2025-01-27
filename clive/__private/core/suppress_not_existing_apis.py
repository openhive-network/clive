from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

from helpy.exceptions import CommunicationError

if TYPE_CHECKING:
    from types import TracebackType


class SuppressNotExistingApis:
    _API_NOT_FOUND_REGEX: Final[str] = (
        r"'Assert Exception:api_itr != data\._registered_apis\.end\(\): Could not find API (\w+_api)'"
    )

    def __init__(self, *api_names: str) -> None:
        self.__api_names = api_names

    def __enter__(self) -> None:
        return None

    def __exit__(self, _: type[BaseException] | None, error: BaseException | None, __: TracebackType | None) -> bool:
        if isinstance(error, CommunicationError):
            apis_not_found = set(self.__get_apis_not_found(str(error)))
            not_suppressed_apis = apis_not_found - set(self.__api_names)
            return not bool(not_suppressed_apis)
        return False

    def __get_apis_not_found(self, message: str) -> list[str]:
        return re.findall(self._API_NOT_FOUND_REGEX, message)
