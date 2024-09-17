from dataclasses import dataclass
from typing import Any, ClassVar

from typing_extensions import Self

from clive.exceptions import CliveError


class CommonOptionInstanceNotAvailableError(CliveError):
    def __init__(self, cls: type["CommonOptionsBase"]) -> None:
        self.cls = cls
        super().__init__(f"Common option instance of {cls.__name__} not available.")


@dataclass
class CommonOptionsBase:
    """
    A base class for sharing common options between commands.

    See: https://github.com/tiangolo/typer/issues/153
    Inspired by: https://github.com/EuleMitKeule/typer-common-options
    """

    instances: ClassVar[dict[type[Self], Self]] = {}

    def __post_init__(self) -> None:
        self.instances[self.__class__] = self  # type: ignore[assignment, index]

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @classmethod
    def get_instance(cls) -> Self:
        if cls not in cls.instances:
            raise CommonOptionInstanceNotAvailableError(cls)

        return cls.instances[cls]

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__
