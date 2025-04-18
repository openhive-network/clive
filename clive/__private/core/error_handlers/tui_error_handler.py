from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeGuard

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.abc.command_in_unlocked import CommandRequiresUnlockedModeError
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ErrorHandlerContextManager,
    ResultNotAvailable,
)

Action = Callable[[], Any]


class TUIErrorHandler(ErrorHandlerContextManager[Exception]):
    def __init__(self) -> None:
        super().__init__()

        self._exception_action_map: dict[type[Exception], Action] = {
            CommandRequiresUnlockedModeError: self._switch_to_locked_mode,
        }

        self._app = get_clive().app_instance()
        self._action: Action | None = None

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[Exception]:
        for exception_type, action in self._exception_action_map.items():
            if isinstance(error, exception_type):
                self._action = action
                return True
        return False

    def _handle_error(self, error: Exception) -> ResultNotAvailable:
        if self._action is not None:
            self._action()
        return ResultNotAvailable(error)

    def _switch_to_locked_mode(self) -> None:
        async def impl() -> None:
            await self._app.switch_mode_into_locked(save_profile=False)

        self._app.run_worker_with_screen_remove_guard(impl())
