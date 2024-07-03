from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast, get_args, overload

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
        self, *, setting_name: str, expected_type: type[object] | tuple[type[object], ...], actual_type: type[object]
    ) -> None:
        self.setting_name = setting_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.message = f"Value of ({setting_name}) should be a type of: {expected_type}, but was: {actual_type}."
        super().__init__(self.message)


class SettingsValueError(SettingsError):
    def __init__(self, *, setting_name: str, value: object, details: str = "") -> None:
        self.setting_name = setting_name
        self.value = value
        self.details = details
        self.message = f"Value of ({setting_name}) is invalid: `{value}`. {details}".strip()
        super().__init__(self.message)


class SafeSettings:
    AvailableLogLevels = _AvailableLogLevels
    AvailableLogLevelsContainer = _AvailableLogLevelsContainer
    AVAILABLE_LOG_LEVELS = _AVAILABLE_LOG_LEVELS

    @dataclass
    class _Dev:
        _parent: SafeSettings

        @property
        def is_set(self) -> bool:
            return self._parent._get_or_default_false("IS_DEV")

        @property
        def should_force_onboarding(self) -> bool:
            return self._parent._get_or_default_false("FORCE_ONBOARDING")

        @property
        def should_enable_debug_loop(self) -> bool:
            return self._parent._get_or_default_false("LOG_DEBUG_LOOP")

        @property
        def debug_loop_period_secs(self) -> float:
            return self._get_log_debug_period_secs()

        def _get_log_debug_period_secs(self) -> float:
            setting_name = "LOG_DEBUG_PERIOD_SECS"
            return self._parent._get_number(setting_name, default=1)

    @dataclass
    class _Log:
        _parent: SafeSettings

        @property
        def path(self) -> Path:
            return self._get_log_path()

        @property
        def levels(self) -> list[_AvailableLogLevels]:
            return self._get_log_levels()

        @property
        def level_3rd_party(self) -> _AvailableLogLevels:
            return self._get_log_level_3rd_party()

        @property
        def should_keep_history(self) -> bool:
            return self._parent._get_or_default_false("LOG_KEEP_HISTORY")

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

        def _get_log_path(self) -> Path:
            setting_name = "LOG_PATH"
            value = settings.get(setting_name)
            message = "log path is set dynamically and always ensured, so should be available now"
            assert isinstance(value, Path), message
            return value

        def _assert_log_levels(self, setting_name: str, *, value: object) -> None:
            self._parent._assert_is_list(setting_name, value=value)
            log_levels = cast(list[object], value)
            for log_level in log_levels:
                self._assert_log_level(setting_name, value=log_level)

        def _assert_log_level(self, setting_name: str, *, value: object) -> None:
            if value not in _AVAILABLE_LOG_LEVELS:
                raise SettingsValueError(
                    setting_name=setting_name, value=value, details=f"Expected one of {_AVAILABLE_LOG_LEVELS}"
                )

    @dataclass
    class _Secrets:
        _parent: SafeSettings

        @property
        def node_address(self) -> Url | None:
            return self._get_secrets_node_address()

        @property
        def default_private_key(self) -> str | None:
            return self._get_secrets_default_private_key()

        def _get_secrets_node_address(self) -> Url | None:
            setting_name = "SECRETS.NODE_ADDRESS"
            return self._parent._get_url(setting_name)

        def _get_secrets_default_private_key(self) -> str | None:
            from clive.__private.core.keys import PrivateKey

            setting_name = "SECRETS.DEFAULT_PRIVATE_KEY"
            value = settings.get(setting_name, "")
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast(str, value)
            if not PrivateKey.is_valid(value_):
                details = "Private key should be a valid private key."
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

    @dataclass
    class _Beekeeper:
        _parent: SafeSettings

        @property
        def path(self) -> Path | None:
            return self._get_beekeeper_path()

        @property
        def remote_address(self) -> Url | None:
            return self._get_beekeeper_remote_address()

        @property
        def communication_total_timeout_secs(self) -> float:
            return self._get_beekeeper_communication_total_timeout_secs()

        @property
        def initialization_timeout_secs(self) -> float:
            return self._get_beekeeper_initialization_timeout_secs()

        def _get_beekeeper_path(self) -> Path | None:
            setting_name = "BEEKEEPER.PATH"
            value = settings.get(setting_name, "")
            if not value:
                return None

            value_ = Path(value)
            self._parent._assert_path_is_file(setting_name, value=value_)
            return value_

        def _get_beekeeper_remote_address(self) -> Url | None:
            setting_name = "BEEKEEPER.REMOTE_ADDRESS"
            return self._parent._get_url(setting_name)

        def _get_beekeeper_communication_total_timeout_secs(self) -> float:
            setting_name = "BEEKEEPER.COMMUNICATION_TOTAL_TIMEOUT_SECS"
            return self._parent._get_number(setting_name, default=3)

        def _get_beekeeper_initialization_timeout_secs(self) -> float:
            setting_name = "BEEKEEPER.INITIALIZATION_TIMEOUT_SECS"
            return self._parent._get_number(setting_name, default=5)

    @dataclass
    class _Node:
        _parent: SafeSettings

        @property
        def chain_id(self) -> str | None:
            return self._get_node_chain_id()

        @property
        def refresh_rate_secs(self) -> float:
            return self._get_node_refresh_rate_secs()

        @property
        def refresh_alarms_rate_secs(self) -> float:
            return self._get_node_refresh_alarms_rate_secs()

        @property
        def communication_timeout_total_secs(self) -> float:
            return self._get_node_communication_timeout_total_secs()

        def _get_node_chain_id(self) -> str | None:
            from clive.__private.core.validate_schema_field import is_schema_field_valid
            from clive.models.aliased import ChainIdSchema

            setting_name = "NODE.CHAIN_ID"
            value = settings.get(setting_name, "")
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast(str, value)

            if not is_schema_field_valid(ChainIdSchema, value_):
                details = f"Chain ID should be {ChainIdSchema.max_length} characters long."
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

        def _get_node_refresh_rate_secs(self) -> float:
            setting_name = "NODE.REFRESH_RATE_SECS"
            return self._parent._get_number(setting_name, default=1.5)

        def _get_node_refresh_alarms_rate_secs(self) -> float:
            setting_name = "NODE.REFRESH_ALARMS_RATE_SECS"
            return self._parent._get_number(setting_name, default=30)

        def _get_node_communication_timeout_total_secs(self) -> float:
            setting_name = "NODE.COMMUNICATION_TOTAL_TIMEOUT_SECS"
            return self._parent._get_number(setting_name, default=6)

    def __init__(self) -> None:
        self.dev = self._Dev(self)
        self.log = self._Log(self)
        self.secrets = self._Secrets(self)
        self.beekeeper = self._Beekeeper(self)
        self.node = self._Node(self)

    @property
    def data_path(self) -> Path:
        return self._get_data_path()

    @property
    def max_number_of_tracked_accounts(self) -> int:
        return self._get_max_number_of_tracked_accounts()

    def _get_data_path(self) -> Path:
        setting_name = "DATA_PATH"
        value = settings.get(setting_name)
        assert isinstance(value, Path), "data path should is set by us, so should be available now"
        return value

    def _get_max_number_of_tracked_accounts(self) -> int:
        setting_name = "MAX_NUMBER_OF_TRACKED_ACCOUNTS"
        return int(self._get_number(setting_name, default=6))

    def _get_or_default_false(self, setting_name: str) -> bool:
        value = settings.get(setting_name, False)
        self._assert_is_bool(setting_name, value=value)
        return cast(bool, value)

    def _get_number(self, setting_name: str, *, default: float) -> float:
        value = settings.get(setting_name, default)
        self._assert_is_number(setting_name, value=value)
        return float(value)

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[False]) -> Url: ...

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[True] = True) -> Url | None: ...

    def _get_url(self, setting_name: str, *, optionally: bool = True) -> Url | None:
        value = settings.get(setting_name, "")
        if not value:
            if optionally:
                return None
            raise SettingsValueError(setting_name=setting_name, value=value, details="URL is required.")

        try:
            return Url.parse(value)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _assert_is_bool(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=bool)

    def _assert_is_string(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=str)

    def _assert_is_number(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=(int, float))

    def _assert_is_list(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=list)

    def _assert_path_is_file(self, setting_name: str, *, value: Path) -> None:
        if not value.is_file():
            raise SettingsValueError(setting_name=setting_name, value=value, details="Path should be a file.")

    def _assert_is_type(
        self, setting_name: str, *, value: object, expected_type: type[object] | tuple[type[object], ...]
    ) -> None:
        if not isinstance(value, expected_type):
            raise SettingsTypeError(setting_name=setting_name, expected_type=expected_type, actual_type=type(value))


safe_settings = SafeSettings()
