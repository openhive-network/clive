from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from clive.__private.core.commands.abc.command_observable import CommandObservable, SenderT
from clive.__private.core.commands.abc.command_with_result import CommandResultT
from clive.__private.core.commands.activate_extended import ActivateExtended
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


ConfirmationCallbackT = Callable[["CommandSecured"], None]
ConfirmationCallbackOptionalT = ConfirmationCallbackT | None


@dataclass(kw_only=True)
class CommandSecured(CommandObservable[CommandResultT], ABC):
    """
    A command that requires a password to proceed.
    """

    confirmation_callback: ClassVar[ConfirmationCallbackOptionalT] = None

    _password: str = field(init=False, repr=False)

    app_state: AppState

    action_name: str = field(init=False)

    @property
    def is_armed(self) -> bool:
        return bool(self._password)

    @classmethod
    def register_confirmation_callback(cls, callback: ConfirmationCallbackT) -> None:
        cls.confirmation_callback = callback

    def execute(self) -> None:
        assert self.confirmation_callback is not None, "The confirmation_callback is not set!"

        command = ActivateExtended(app_state=self.app_state)
        command.observe_result(self.__on_activation_result)
        command.execute()

    def _arm(self, **kwargs: Any) -> None:
        self._password = kwargs.get("password", "")

    def __on_activation_result(
        self, _: SenderT, result: bool | None, exception: Exception | None  # noqa: ARG002
    ) -> None:
        logger.debug(f"Command requires confirmation: {self.__class__.__name__}")
        if result:
            assert self.confirmation_callback is not None, "The confirmation_callback is not set!"
            self.confirmation_callback(self)  # the callback should call CommandSecured.fire()
