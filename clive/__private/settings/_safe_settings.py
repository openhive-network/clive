from __future__ import annotations

import ast
from abc import ABC
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, cast, get_args, overload

import beekeepy as bk
import beekeepy.handle.remote as bkhr
import beekeepy.interfaces as bki
from inflection import underscore

from clive.__private.core.constants.setting_identifiers import (
    BEEKEEPER_CLOSE_TIMEOUT,
    BEEKEEPER_COMMUNICATION_ATTEMPTS_AMOUNT,
    BEEKEEPER_COMMUNICATION_RETRIES_DELAY_SECS,
    BEEKEEPER_COMMUNICATION_TOTAL_TIMEOUT_SECS,
    BEEKEEPER_INITIALIZATION_TIMEOUT,
    BEEKEEPER_REFRESH_TIMEOUT_SECS,
    BEEKEEPER_REMOTE_ADDRESS,
    BEEKEEPER_SESSION_TOKEN,
    DATA_PATH,
    IS_DEV,
    LOG_DEBUG_LOOP,
    LOG_DEBUG_PERIOD_SECS,
    LOG_DIRECTORY,
    LOG_KEEP_HISTORY,
    LOG_LEVEL_1ST_PARTY,
    LOG_LEVEL_3RD_PARTY,
    LOG_LEVELS,
    MAX_NUMBER_OF_TRACKED_ACCOUNTS,
    NODE_CHAIN_ID,
    NODE_COMMUNICATION_ATTEMPTS_AMOUNT,
    NODE_COMMUNICATION_RETRIES_DELAY_SECS,
    NODE_COMMUNICATION_TOTAL_TIMEOUT_SECS,
    NODE_REFRESH_ALARMS_RATE_SECS,
    NODE_REFRESH_RATE_SECS,
    SECRETS_DEFAULT_PRIVATE_KEY,
    SECRETS_NODE_ADDRESS,
    SELECT_FILE_ROOT_PATH,
)
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.settings._settings import get_settings
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from beekeepy import InterfaceSettings as BeekeepySettings
    from beekeepy.handle.remote import RemoteHandleSettings
    from beekeepy.interfaces import HttpUrl

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


class NotSet:
    """Used to represent a value that has not been set."""


NOT_SET: Final[NotSet] = NotSet()


class SafeSettings:
    AvailableLogLevels = _AvailableLogLevels
    AvailableLogLevelsContainer = _AvailableLogLevelsContainer
    AVAILABLE_LOG_LEVELS = _AVAILABLE_LOG_LEVELS

    @dataclass
    class _Namespace(ABC):
        _parent: SafeSettings

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
        def level_1st_party(self) -> _AvailableLogLevels:
            return self._get_log_level_1st_party()

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
            return cast("_AvailableLogLevelsContainer", value)

        def _get_log_level_1st_party(self) -> _AvailableLogLevels:
            setting_name = LOG_LEVEL_1ST_PARTY
            value = self._parent._get_value_from_settings(setting_name, "INFO")
            self._assert_log_level(setting_name, value=value)
            return cast("_AvailableLogLevels", value)

        def _get_log_level_3rd_party(self) -> _AvailableLogLevels:
            setting_name = LOG_LEVEL_3RD_PARTY
            value = self._parent._get_value_from_settings(setting_name, "WARNING")
            self._assert_log_level(setting_name, value=value)
            return cast("_AvailableLogLevels", value)

        def _get_log_path(self) -> Path:
            value = self._parent._get_path(LOG_DIRECTORY, default=self._parent.data_path)
            return value / "logs"

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
        def node_address(self) -> HttpUrl | None:
            return self._get_secrets_node_address()

        @property
        def default_private_key(self) -> str | None:
            return self._get_secrets_default_private_key()

        def _get_secrets_node_address(self) -> HttpUrl | None:
            return self._parent._get_url(SECRETS_NODE_ADDRESS)

        def _get_secrets_default_private_key(self) -> str | None:
            from clive.__private.core.keys import PrivateKey  # noqa: PLC0415

            setting_name = SECRETS_DEFAULT_PRIVATE_KEY
            value = self._parent._get_value_from_settings(setting_name, optionally=True)
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast("str", value)
            if not PrivateKey.is_valid(value_):
                details = "Private key should be a valid private key."
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

    @dataclass
    class _Beekeeper(_Namespace):
        @property
        def remote_address(self) -> HttpUrl | None:
            return self._get_beekeeper_remote_address()

        @property
        def is_remote_address_set(self) -> bool:
            return self.remote_address is not None

        @property
        def should_start_locally(self) -> bool:
            return not self.is_remote_address_set

        @property
        def communication_total_timeout_secs(self) -> float:
            return self._get_beekeeper_communication_total_timeout_secs()

        @property
        def communication_attempts_amount(self) -> int:
            return self._get_beekeeper_communication_attempts_amount()

        @property
        def communication_retries_delay_secs(self) -> float:
            return self._get_beekeeper_communication_retries_delay_secs()

        @property
        def refresh_timeout_secs(self) -> float:
            return self._get_beekeeper_refresh_timeout_secs()

        @property
        def working_directory(self) -> Path:
            return self._get_beekeeper_working_directory()

        @property
        def session_token(self) -> str | None:
            return self._get_beekeeper_session_token()

        @property
        def initialization_timeout(self) -> float:
            return self._get_beekeeper_initialization_timeout()

        @property
        def close_timeout(self) -> float:
            return self._get_beekeeper_close_timeout()

        @property
        def is_session_token_set(self) -> bool:
            return self.session_token is not None

        def settings_remote_factory(self) -> BeekeepySettings:
            beekeepy_settings = bk.InterfaceSettings()

            beekeepy_settings.working_directory = self.working_directory
            beekeepy_settings.http_endpoint = self.remote_address
            beekeepy_settings.use_existing_session = self.session_token
            beekeepy_settings.timeout = timedelta(seconds=self.communication_total_timeout_secs)
            beekeepy_settings.max_retries = self.communication_attempts_amount
            beekeepy_settings.period_between_retries = timedelta(seconds=self.communication_retries_delay_secs)
            beekeepy_settings.initialization_timeout = timedelta(seconds=self.initialization_timeout)
            beekeepy_settings.close_timeout = timedelta(seconds=self.close_timeout)
            beekeepy_settings.propagate_sigint = False

            return beekeepy_settings

        def settings_local_factory(self) -> BeekeepySettings:
            beekeepy_settings = self.settings_remote_factory()
            beekeepy_settings.http_endpoint = None
            beekeepy_settings.use_existing_session = None
            return beekeepy_settings

        def settings_factory(self) -> BeekeepySettings:
            return self.settings_local_factory() if self.should_start_locally else self.settings_remote_factory()

        def _get_beekeeper_remote_address(self) -> HttpUrl | None:
            return self._parent._get_url(BEEKEEPER_REMOTE_ADDRESS)

        def _get_beekeeper_communication_total_timeout_secs(self) -> float:
            return self._parent._get_number(BEEKEEPER_COMMUNICATION_TOTAL_TIMEOUT_SECS, default=15, minimum=1)

        def _get_beekeeper_communication_attempts_amount(self) -> int:
            return int(self._parent._get_number(BEEKEEPER_COMMUNICATION_ATTEMPTS_AMOUNT, default=1, minimum=1))

        def _get_beekeeper_communication_retries_delay_secs(self) -> float:
            return self._parent._get_number(BEEKEEPER_COMMUNICATION_RETRIES_DELAY_SECS, default=0.2, minimum=0)

        def _get_beekeeper_refresh_timeout_secs(self) -> float:
            return self._parent._get_number(BEEKEEPER_REFRESH_TIMEOUT_SECS, default=0.5, minimum=0.1)

        def _get_beekeeper_working_directory(self) -> Path:
            return self._parent._get_data_path() / "beekeeper"

        def _get_beekeeper_session_token(self) -> str | None:
            beekeeper_session_token = self._parent._get_value_from_settings(BEEKEEPER_SESSION_TOKEN, optionally=True)
            if beekeeper_session_token:
                return str(beekeeper_session_token)
            return None

        def _get_beekeeper_initialization_timeout(self) -> float:
            return self._parent._get_number(BEEKEEPER_INITIALIZATION_TIMEOUT, default=5, minimum=1)

        def _get_beekeeper_close_timeout(self) -> float:
            return self._parent._get_number(BEEKEEPER_CLOSE_TIMEOUT, default=5, minimum=1)

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

        @property
        def communication_attempts_amount(self) -> int:
            return self._get_node_communication_attempts_amount()

        @property
        def communication_retries_delay_secs(self) -> float:
            return self._get_node_communication_retries_delay_secs()

        def settings_factory(self, http_endpoint: HttpUrl) -> RemoteHandleSettings:
            remote_handle_settings = bkhr.RemoteHandleSettings(http_endpoint=http_endpoint)

            remote_handle_settings.timeout = timedelta(seconds=self.communication_timeout_total_secs)
            remote_handle_settings.max_retries = self.communication_attempts_amount
            remote_handle_settings.period_between_retries = timedelta(seconds=self.communication_retries_delay_secs)

            return remote_handle_settings

        def _get_node_chain_id(self) -> str | None:
            from clive.__private.models.schemas import ChainId, is_matching_model  # noqa: PLC0415

            setting_name = NODE_CHAIN_ID
            value = self._parent._get_value_from_settings(setting_name, optionally=True)
            if not value:
                return None

            self._parent._assert_is_string(setting_name, value=value)
            value_ = cast("str", value)

            if not is_matching_model(value_, ChainId):
                details = f"Chain ID should be {ChainId.meta().max_length} characters long."  # type: ignore[attr-defined]
                raise SettingsValueError(setting_name=setting_name, value=value_, details=details)
            return value_

        def _get_node_refresh_rate_secs(self) -> float:
            return self._parent._get_number(NODE_REFRESH_RATE_SECS, default=1.5, minimum=1)

        def _get_node_refresh_alarms_rate_secs(self) -> float:
            return self._parent._get_number(NODE_REFRESH_ALARMS_RATE_SECS, default=30, minimum=5)

        def _get_node_communication_timeout_total_secs(self) -> float:
            return self._parent._get_number(NODE_COMMUNICATION_TOTAL_TIMEOUT_SECS, default=30, minimum=1)

        def _get_node_communication_attempts_amount(self) -> int:
            return int(self._parent._get_number(NODE_COMMUNICATION_ATTEMPTS_AMOUNT, default=5, minimum=1))

        def _get_node_communication_retries_delay_secs(self) -> float:
            return self._parent._get_number(NODE_COMMUNICATION_RETRIES_DELAY_SECS, default=0.2, minimum=0)

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
    def select_file_root_path(self) -> Path:
        return self._get_select_file_root_path()

    @property
    def custom_bindings_path(self) -> Path:
        return self.data_path / "custom_bindings.toml"

    @property
    def default_bindings_path(self) -> Path:
        return self.data_path / "default_bindings.toml"

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

    def _create_namespace[T: SafeSettings._Namespace](self, namespace: type[T]) -> T:
        self._namespaces.add(namespace)
        return namespace(self)

    def _get_path(self, setting_name: str, default: Path | NotSet = NOT_SET) -> Path:
        value = self._get_value_from_settings(setting_name, default)
        if isinstance(value, Path):
            # case when value is set in runtime, by us
            return value
        # case when value is overridden by environment variable
        self._assert_is_string(setting_name, value=value)
        value_ = cast("str", value)
        return Path(value_)

    def _get_data_path(self) -> Path:
        return self._get_path(DATA_PATH)

    def _get_select_file_root_path(self) -> Path:
        return self._get_path(SELECT_FILE_ROOT_PATH, Path.home())

    def _get_max_number_of_tracked_accounts(self) -> int:
        return int(self._get_number(MAX_NUMBER_OF_TRACKED_ACCOUNTS, default=6, minimum=1))

    def _get_or_default_false(self, setting_name: str) -> bool:
        return self._get_bool(setting_name, default=False)

    def _get_bool(self, setting_name: str, *, default: bool | NotSet = NOT_SET) -> bool:
        value = self._get_value_from_settings(setting_name, default=default)

        try:
            return bool(value)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _get_number(
        self, setting_name: str, *, default: float | NotSet = NOT_SET, minimum: float | None = None
    ) -> float:
        from textual.validation import Number  # noqa: PLC0415

        value = self._get_value_from_settings(setting_name, default=default)
        value_ = str(value)
        result = Number(minimum=minimum).validate(value_)
        if not result.is_valid:
            raise SettingsValueError(
                setting_name=setting_name, value=value_, details=humanize_validation_result(result)
            )

        return float(value_)

    def _get_list(self, setting_name: str, default: object | NotSet = NOT_SET) -> list[object]:
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
        return cast("list[object]", value_)

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[False]) -> HttpUrl: ...

    @overload
    def _get_url(self, setting_name: str, *, optionally: Literal[True] = True) -> HttpUrl | None: ...

    def _get_url(self, setting_name: str, *, optionally: bool = True) -> HttpUrl | None:
        value = self._get_value_from_settings(setting_name, optionally=optionally)
        if not value:
            return None

        self._assert_is_string(setting_name, value=value)
        value_ = cast("str", value)
        try:
            return bki.HttpUrl(value_)
        except Exception as error:
            raise SettingsValueError(setting_name=setting_name, value=value, details=str(error)) from error

    def _get_value_from_settings(
        self, setting_name: str, default: object | NotSet = NOT_SET, *, optionally: bool = False
    ) -> object:
        # Call .get(setting_name, default) will only return the default value when the setting/envvar doesn't exist,
        #  not when is set to empty string.
        value = get_settings().get(setting_name)
        if value in ("", None):
            if default is not NOT_SET:
                return default
            if optionally:
                return None

            raise SettingsValueError(setting_name=setting_name, value=value, details="Value is required.")

        return value

    def _assert_is_string(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=str)

    def _assert_is_list(self, setting_name: str, *, value: object) -> None:
        self._assert_is_type(setting_name=setting_name, value=value, expected_type=list)

    def _assert_is_type(
        self, setting_name: str, *, value: object, expected_type: type[object] | tuple[type[object], ...]
    ) -> None:
        if not isinstance(value, expected_type):
            raise SettingsTypeError(setting_name=setting_name, expected_type=expected_type, actual_type=type(value))


safe_settings = SafeSettings()
