from __future__ import annotations

from pathlib import Path
from types import UnionType
from typing import TYPE_CHECKING, get_args

from pydantic import Field

from clive.__private.config import settings
from clive.__private.core.beekeeper.defaults import BeekeeperDefaults
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models.base import CliveBaseModel

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.command_line_args import ExportKeysWalletParams

AllowedTypesT = str | list[str] | bool | int | Url | Path


class InvalidOptionError(CliveError):
    pass


def webserver_default() -> Url:
    return Url("http", "0.0.0.0", 0)


def _wallet_dir_default() -> Path:
    return Path(settings.data_path) / "beekeeper"


class BeekeeperConfig(CliveBaseModel):
    wallet_dir: Path = Field(default_factory=_wallet_dir_default)
    unlock_timeout: int = BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT
    log_json_rpc: Path | None = BeekeeperDefaults.DEFAULT_LOG_JSON_RPC
    webserver_http_endpoint: Url | None = Field(default_factory=webserver_default)
    webserver_unix_endpoint: Url | None = None
    webserver_ws_endpoint: Url | None = None
    webserver_ws_deflate: int = 0
    webserver_thread_pool_size: int = 1
    webserver_https_endpoint: Url | None = None
    webserver_https_certificate_file_name: Path | None = None
    webserver_https_key_file_name: Path | None = None
    notifications_endpoint: Url | None = BeekeeperDefaults.DEFAULT_NOTIFICATIONS_ENDPOINT
    backtrace: str = BeekeeperDefaults.DEFAULT_BACKTRACE
    plugin: list[str] = Field(default_factory=lambda: ["json_rpc", "webserver"])
    export_keys_wallet: ExportKeysWalletParams | None = BeekeeperDefaults.DEFAULT_EXPORT_KEYS_WALLET

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def get_wallet_dir() -> Path:
        return _wallet_dir_default()

    def save(self, destination: Path) -> None:
        with destination.open("wt", encoding="utf-8") as out_file:
            out_file.write("# config automatically generated by clive\n")
            for member_name, member_value in self.__dict__.items():
                if member_value is not None:
                    out_file.write(
                        f"{self.__convert_member_name_to_config_name(member_name)}={self.__convert_member_value_to_config_value(member_value)}\n"
                    )

    @classmethod
    def load(cls, source: Path) -> BeekeeperConfig:
        assert source.exists()
        result = BeekeeperConfig()
        fields = BeekeeperConfig.__fields__
        with source.open("rt", encoding="utf-8") as in_file:
            for line in in_file:
                if (line := line.strip("\n")) and not line.startswith("#"):
                    config_name, config_value = line.split("=")
                    member_name = cls.__convert_config_name_to_member_name(config_name)
                    member_type = fields[member_name].annotation
                    if isinstance(member_type, UnionType) and get_args(member_type)[-1] == type(None):
                        member_type = get_args(member_type)[0]
                    setattr(
                        result,
                        member_name,
                        cls.__convert_config_value_to_member_value(config_value, expected=member_type),
                    )
        return result

    @classmethod
    def __convert_member_name_to_config_name(cls, member_name: str) -> str:
        return member_name.replace("_", "-")

    @classmethod
    def __convert_config_name_to_member_name(cls, config_name: str) -> str:
        return config_name.strip().replace("-", "_")

    @classmethod
    def __convert_member_value_to_config_value(cls, member_value: AllowedTypesT) -> str:
        if isinstance(member_value, list):
            return " ".join(member_value)

        if isinstance(member_value, bool):
            return "yes" if member_value else "no"

        if isinstance(member_value, Url):
            return member_value.as_string(with_protocol=False)

        if isinstance(member_value, Path):
            return member_value.as_posix()

        return str(member_value)

    @classmethod
    def __convert_config_value_to_member_value(  # noqa: PLR0911
        cls, config_value: str, *, expected: type[AllowedTypesT]
    ) -> AllowedTypesT | None:
        config_value = config_value.strip()
        if not config_value:
            return None

        if expected == Path:
            return Path(config_value.replace('"', ""))

        if expected == list[str]:
            return config_value.split()

        if expected == Url:
            return Url.parse(config_value)

        if expected == bool:
            cv_lower = config_value.lower()
            if cv_lower == "yes":
                return True

            if cv_lower == "no":
                return False

            raise InvalidOptionError(f"Expected `yes` or `no`, got: `{config_value}`")

        return expected(config_value) if expected is not None else None  # type: ignore[call-arg]
