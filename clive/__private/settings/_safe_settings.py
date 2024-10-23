from __future__ import annotations

import ast
from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar, cast, get_args, overload

from inflection import underscore

from clive.__private.core.constants.setting_identifiers import (
    BEEKEEPER_COMMUNICATION_TOTAL_TIMEOUT_SECS,
    BEEKEEPER_INITIALIZATION_TIMEOUT_SECS,
    BEEKEEPER_PATH,
    BEEKEEPER_REMOTE_ADDRESS,
    BEEKEEPER_SESSION_TOKEN,
    DATA_PATH,
    IS_DEV,
    LOG_DEBUG_LOOP,
    LOG_DEBUG_PERIOD_SECS,
    LOG_KEEP_HISTORY,
    LOG_LEVEL_3RD_PARTY,
    LOG_LEVELS,
    LOG_PATH,
    MAX_NUMBER_OF_TRACKED_ACCOUNTS,
    NODE_CHAIN_ID,
    NODE_COMMUNICATION_TOTAL_TIMEOUT_SECS,
    NODE_REFRESH_ALARMS_RATE_SECS,
    NODE_REFRESH_RATE_SECS,
    SECRETS_DEFAULT_PRIVATE_KEY,
    SECRETS_NODE_ADDRESS,
)
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.url import Url
from clive.__private.settings._settings import settings
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
    class _Namespace(ABC):
        _parent: SafeSettings

    _NamespaceT = TypeVar("_NamespaceT", bound=_Namespace)

    @dataclass
    class _Dev(_Namespace):
        @property
        def is_set(self) -> bool:
            return self._parent._get_or_default_false(IS_DEV)

        @property
        def should_enable_debug_loop(self) -> bool:
            return self._parent._get_or_default_false(LOG_DEBUG_LOOP)

        @property
        def debug_loop_period_secs(self) -> float:
            return self._get_log_debug_period_secs()

        def _get_log_debug_period_secs(self) -> float:
            return self._parent._get_number(LOG_DEBUG_PERIOD_SECS, default=1, minimum=1)

    @dataclass
    class _Log(_Namespace):
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
            return self._parent._get_or_default_false(LOG_KEEP_HISTORY)

        def _get_log_levels(self) -> _AvailableLogLevelsContainer:
            setting_name = LOG_LEVELS
            value = self._parent._get_list(setting_name, ["INFO"])
            self._assert_log_levels(setting_name, value=value)
            return cast(_AvailableLogLevelsContainer, value)

        def _get_log_level_3rd_party(self) -> _AvailableLogLevels:
            setting_name = LOG_LEVEL_3RD_PARTY
            value = self._parent._get_value_from_settings(setting_name, "WARNING")
            self._assert_log_level(setting_name, value=value)
            return cast(_AvailableLogLevels, value)

        def _get_log_path(self) -> Path:
            value = self._parent._get_value_from_settings(LOG_PATH)
            message = "log path is set dynamically and always ensured, so should be available now"
            assert isinstance(value, Path), message
            return value

        def _assert_log_levels(self, setting_name: str, *, value: list[object]) -> None:
            for log_level in value:
                self._assert_log_level(setting_name, value=log_level)

        def _assert_log_level(self, setting_name: str, *, value: object) -> None:
            if value not in _AVAILABLE_LOG_LEVELS:
                raise SettingsValueError(
                    setting_name=setting_name, value=value, details=f"Expected one of {_AVAILABLE_LOG_LEVELS}"
                )

    @dataclass
    class _Secrets(_Namespace):
        @property
        def node_address(self) -> Url | None:
            return self._get_secrets_node_address()

        @property
        def default_private_key(self) -> str | None:
            return self._get_secrets_default_private_key()

        def _get_secrets_node_address(self) -> Url | None:
            return self._parent._get_url(SECRETS_NODE_ADDRESS)

        def _get_secrets_default_private_key(self) -> str | None:
            from clive.__private.core.keys import PrivateKey

            setting_name = SECRETS_DEFAULT_PRIVATE_KEY
            value = self._parent._get_value_from_settings(setting_name, "")
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast(str, value)
            if not PrivateKey.is_valid(value_):
                details = "Private key should be a valid private key."
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

    @dataclass
    class _Beekeeper(_Namespace):
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

        @property
        def session_token(self) -> str | None:
            return self._get_beekeeper_session_token()

        @property
        def is_session_token_set(self) -> bool:
            return self.session_token is not None

        def _get_beekeeper_path(self) -> Path | None:
            setting_name = BEEKEEPER_PATH
            value = self._parent._get_value_from_settings(setting_name, "")
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = Path(cast(str, value))
            self._parent._assert_path_is_file(setting_name, value=value_)
            return value_

        def _get_beekeeper_remote_address(self) -> Url | None:
            return self._parent._get_url(BEEKEEPER_REMOTE_ADDRESS)

        def _get_beekeeper_communication_total_timeout_secs(self) -> float:
            return self._parent._get_number(BEEKEEPER_COMMUNICATION_TOTAL_TIMEOUT_SECS, default=15, minimum=1)

        def _get_beekeeper_initialization_timeout_secs(self) -> float:
            return self._parent._get_number(BEEKEEPER_INITIALIZATION_TIMEOUT_SECS, default=5, minimum=1)

        def _get_beekeeper_session_token(self) -> str | None:
            beekeeper_session_token = self._parent._get_value_from_settings(BEEKEEPER_SESSION_TOKEN, None)
            if beekeeper_session_token:
                return str(beekeeper_session_token)
            return None

    @dataclass
    class _Node(_Namespace):
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
            from clive.__private.models.schemas import ChainId

            setting_name = NODE_CHAIN_ID
            value = self._parent._get_value_from_settings(setting_name, "")
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast(str, value)

            if not is_schema_field_valid(ChainId, value_):
                details = f"Chain ID should be {ChainId.max_length} characters long."
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

        def _get_node_refresh_rate_secs(self) -> float:
            return self._parent._get_number(NODE_REFRESH_RATE_SECS, default=1.5, minimum=1)

        def _get_node_refresh_alarms_rate_secs(self) -> float:
            return self._parent._get_number(NODE_REFRESH_ALARMS_RATE_SECS, default=30, minimum=5)

        def _get_node_communication_timeout_total_secs(self) -> float:
            return self._parent._get_number(NODE_COMMUNICATION_TOTAL_TIMEOUT_SECS, default=30, minimum=1)

    def __init__(self) -> None:
        self._namespaces: set[type[SafeSettings._Namespace]] = set()
        self.dev = self._create_namespace(self._Dev)
        self.log = self._create_namespace(self._Log)
        self.secrets = self._create_namespace(self._Secrets)
        self.beekeeper = self._create_namespace(self._Beekeeper)
        self.node = self._create_namespace(self._Node)

    @property
    def data_path(self) -> Path:
        return self._get_data_path()

    @property
    def max_number_of_tracked_accounts(self) -> int:
        return self._get_max_number_of_tracked_accounts()

    def validate(self) -> None:
        def find_property_names(cls: type[object]) -> list[str]:
            return [k for k, v in vars(cls).items() if isinstance(v, property)]

        for namespace in self._namespaces:
            my_member_name = underscore(namespace.__name__).replace("_", "")
            my_member = getattr(self, my_member_name)

            for prop_name in find_property_names(namespace):
                # call property to run setting validation
                getattr(my_member, prop_name)

        for my_prop_name in find_property_names(self.__class__):
            # call property to run setting validation
            getattr(self, my_prop_name)

    def _create_namespace(self, namespace: type[_NamespaceT]) -> _NamespaceT:
        self._namespaces.add(namespace)
        return namespace(self)

    def _get_data_path(self) -> Path:
        setting_name = DATA_PATH
        value = settings.get(setting_name)
        if isinstance(value, Path):
            # case when value is set in runtime, by us
            return value
        # case when value is overridden by environment variable
        self._assert_is_string(setting_name, value=value)
        return Path(value)

    def _get_max_number_of_tracked_accounts(self) -> int:
        return int(self._get_number(MAX_NUMBER_OF_TRACKED_ACCOUNTS, default=6, minimum=1))

    def _get_or_default_false(self, setting_name: str) -> bool:
        return self._get_bool(setting_name, default=False)

    def _get_bool(self, setting_name: str, *, default: bool | None = None) -> bool:
        value = self._get_value_from_settings(setting_name, default=default)

        try:
            return bool(value)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _get_number(self, setting_name: str, *, default: float | None = None, minimum: float | None = None) -> float:
        from textual.validation import Number

        value = self._get_value_from_settings(setting_name, default=default)
        value_ = str(value)
        result = Number(minimum=minimum).validate(value_)
        if not result.is_valid:
            raise SettingsValueError(
                setting_name=setting_name, value=value_, details=humanize_validation_result(result)
            )

        return float(value_)

    def _get_list(self, setting_name: str, default: object | None = None) -> list[object]:
        value = self._get_value_from_settings(setting_name, default=default)
        if isinstance(value, str):
            # try to parse string as list
            try:
                value_ = ast.literal_eval(value)
            except Exception as error:
                raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error
        else:
            value_ = value
        self._assert_is_list(setting_name, value=value_)
        return cast(list[object], value_)

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[False]) -> Url: ...

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[True] = True) -> Url | None: ...

    def _get_url(self, setting_name: str, *, optionally: bool = True) -> Url | None:
        value = self._get_value_from_settings(setting_name, "")
        if not value:
            if optionally:
                return None
            raise SettingsValueError(setting_name=setting_name, value=value, details="URL is required.")

        self._assert_is_string(setting_name, value=value)
        value_ = cast(str, value)
        try:
            return Url.parse(value_)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _get_value_from_settings(self, setting_name: str, default: object | None = None) -> object:
        return settings.get(setting_name) if default is None else settings.get(setting_name, default)

    def _assert_is_string(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=str)

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
