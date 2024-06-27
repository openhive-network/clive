from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, cast, get_args

from clive.__private.config import settings
from clive.core.url import Url
from clive.exceptions import CliveError

_AvailableLogLevels = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
_AvailableLogLevelsContainer = list[_AvailableLogLevels]
_AVAILABLE_LOG_LEVELS: tuple[_AvailableLogLevels, ...] = get_args(_AvailableLogLevels)


class SettingsError(CliveError):
    pass


class SettingsTypeError(SettingsError):
    def __init__(
        self, *, setting_name: str, expected_type: type[Any] | tuple[type[Any], ...], actual_type: type[Any]
    ) -> None:
        self.setting_name = setting_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.message = f"Value of ({setting_name}) should be a type of: {expected_type}, but was: {actual_type}."
        super().__init__(self.message)


class SettingsValueError(SettingsError):
    def __init__(self, *, setting_name: str, value: Any, details: str = "") -> None:  # noqa: ANN401
        self.setting_name = setting_name
        self.value = value
        self.details = details
        self.message = f"Value of ({setting_name})  is invalid: {value}. {details}".strip()
        super().__init__(self.message)


class SafeSettings:
    AvailableLogLevels = _AvailableLogLevels
    AvailableLogLevelsContainer = _AvailableLogLevelsContainer
    AVAILABLE_LOG_LEVELS = _AVAILABLE_LOG_LEVELS

    @property
    def is_dev(self) -> bool:
        return self._get_or_default_false("IS_DEV")

    @property
    def force_onboarding(self) -> bool:
        return self._get_or_default_false("FORCE_ONBOARDING")

    @property
    def log_levels(self) -> list[_AvailableLogLevels]:
        return self._get_log_levels()

    @property
    def log_level_3rd_party(self) -> _AvailableLogLevels:
        return self._get_log_level_3rd_party()

    @property
    def log_keep_history(self) -> bool:
        return self._get_or_default_false("LOG_KEEP_HISTORY")

    @property
    def log_debug_loop(self) -> bool:
        return self._get_or_default_false("LOG_DEBUG_LOOP")

    @property
    def log_debug_loop_period_secs(self) -> float:
        return self._get_log_debug_period_secs()

    @property
    def log_path(self) -> Path:
        return self._get_log_path()

    @property
    def beekeeper_path(self) -> Path | None:
        return self._get_beekeeper_path()

    @property
    def beekeeper_remote_address(self) -> Url | None:
        return self._get_beekeeper_remote_address()

    def _get_or_default_false(self, setting_name: str) -> bool:
        value = settings.get(setting_name, False)
        self._assert_is_bool(setting_name, value=value)
        return cast(bool, value)

    def _get_log_levels(self) -> _AvailableLogLevelsContainer:
        setting_name = "LOG_LEVELS"
        value = settings.get(setting_name, ["INFO"])
        self._assert_log_levels(setting_name, value=value)
        return cast(_AvailableLogLevelsContainer, value)

    def _get_log_level_3rd_party(self) -> _AvailableLogLevels:
        setting_name = "LOG_LEVEL_3RD_PARTY"
        value = settings.get(setting_name, "WARNING")
        self._assert_log_level(setting_name, value=value)
        return cast(_AvailableLogLevels, value)

    def _get_log_debug_period_secs(self) -> float:
        setting_name = "LOG_DEBUG_PERIOD_SECS"
        value = settings.get(setting_name, 1)
        self._assert_is_number(setting_name, value=value)
        return cast(float, value)

    def _get_log_path(self) -> Path:
        setting_name = "LOG_PATH"
        value = settings.get(setting_name)
        assert isinstance(value, Path), "log path should is set dynamically, so should be available now"
        return value

    def _get_beekeeper_path(self) -> Path | None:
        setting_name = "BEEKEEPER.PATH"
        value = settings.get(setting_name, "")
        if not value:
            return None

        value_ = Path(value)
        self._assert_path_is_file(setting_name, value=value_)
        return value_

    def _get_beekeeper_remote_address(self) -> Url | None:
        setting_name = "BEEKEEPER.REMOTE_ADDRESS"
        value = settings.get(setting_name, "")
        if not value:
            return None

        try:
            return Url.parse(value)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _assert_log_levels(self, setting_name: str, *, value: object) -> None:
        self._assert_is_list(setting_name, value=value)
        value = cast(list[Any], value)
        for log_level in value:
            self._assert_log_level(setting_name, value=log_level)

    def _assert_log_level(self, setting_name: str, *, value: object) -> None:
        if value not in _AVAILABLE_LOG_LEVELS:
            raise SettingsValueError(
                setting_name=setting_name, value=value, details=f"Expected one of {_AVAILABLE_LOG_LEVELS}"
            )

    def _assert_is_bool(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=bool)

    def _assert_is_number(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=(int, float))

    def _assert_is_list(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=list)

    def _assert_path_is_file(self, setting_name: str, *, value: Path) -> None:
        if not value.is_file():
            raise SettingsValueError(setting_name=setting_name, value=value, details="Path should be a file.")

    def _assert_is_type(
        self, setting_name: str, *, value: object, expected_type: type[Any] | tuple[type[Any], ...]
    ) -> None:
        if not isinstance(value, expected_type):
            raise SettingsTypeError(setting_name=setting_name, expected_type=expected_type, actual_type=type(value))


safe_settings = SafeSettings()
