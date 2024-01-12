from __future__ import annotations

import os
from pathlib import Path

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.defaults import BeekeeperDefaults


def check_default_values_from_config(default_config: BeekeeperConfig) -> None:
    assert default_config.wallet_dir.resolve() == BeekeeperDefaults.DEFAULT_WALLET_DIR.resolve()
    assert default_config.unlock_timeout == BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT
    assert default_config.log_json_rpc == BeekeeperDefaults.DEFAULT_LOG_JSON_RPC
    assert default_config.webserver_http_endpoint == webserver_default()
    assert default_config.webserver_thread_pool_size == BeekeeperDefaults.DEFAULT_WEBSERVER_THREAD_POOL_SIZE
    assert default_config.notifications_endpoint == BeekeeperDefaults.DEFAULT_NOTIFICATIONS_ENDPOINT
    assert default_config.backtrace == BeekeeperDefaults.DEFAULT_BACKTRACE
    assert default_config.export_keys_wallet == BeekeeperDefaults.DEFAULT_EXPORT_KEYS_WALLET
    assert default_config.webserver_https_endpoint == BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_ENDPOINT
    assert (
        default_config.webserver_https_certificate_file_name
        == BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME
    )
    assert default_config.webserver_https_key_file_name == BeekeeperDefaults.DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME


async def test_default_values() -> None:
    """Test will check default values of Beekeeper."""
    # ARRANGE & ACT
    default_config = Beekeeper().generate_beekeepers_default_config()

    # ASSERT
    check_default_values_from_config(default_config)


def extract_fields_and_values(help_message: list[str]) -> dict[str, str | None]:
    """Main function for extracting arguments and default values from help message."""

    def __extract_name(split: list[str]) -> str | None:
        """Extract argument name from help."""
        help_line_len_with_single_argument = 2
        if len(split) > help_line_len_with_single_argument and "--" in split[2] and "-" in split[0]:
            return split[2].removeprefix("--").replace("-", "_")
        if "--" in split[0]:
            return split[0].removeprefix("--").replace("-", "_")
        return None

    def __extract_value(split: list[str], description_line: str | None = None) -> str | None:
        """Extract default value for argument from help."""
        if split[-1].startswith("(="):
            default_value = split[-1].strip('"()')
            return default_value.split("=")[-1].strip('"')
        if description_line:
            # default value is in description. unfortunately according to Mariusz, there is no way to unify default in help:
            # data-dir has structure "Directory containing configuration file config.ini. Default location: $HOME/." << app_name << " or CWD/. " << app_name; application.cpp:135
            default_path = "$HOME/.beekeeper"
            start = description_line.find(default_path)
            return os.path.expandvars(description_line[start : start + len(default_path)])
        return None

    help_fields = {}
    for nr, line in enumerate(help_message):
        if "--" not in line:
            continue
        split = line.strip().strip("\n").split(" ")
        field_name = __extract_name(split)
        if field_name is None:
            continue
        description_line = help_message[nr + 1] if field_name == "data_dir" else None
        field_value = __extract_value(split, description_line=description_line)

        help_fields[field_name] = field_value
    return help_fields


async def test_help_fields_coverege() -> None:
    """Test will check arguments and its values extracted from help message."""
    # ARRANGE & ACT
    help_fields = extract_fields_and_values(Beekeeper().help().split("\n"))
    default_fields = {attr: getattr(BeekeeperDefaults, attr) for attr, _ in BeekeeperDefaults.__annotations__.items()}

    # ASSERT
    assert len(help_fields) > 0, "There should be some arguments extracted from help."
    for help_field_name, help_field_value in help_fields.items():
        class_default_value = default_fields.pop(f"DEFAULT_{help_field_name.upper()}")
        value: int | str | Path | None = help_field_value
        if isinstance(class_default_value, int) and help_field_value:
            value = int(help_field_value)
        elif isinstance(class_default_value, Path) and help_field_value:
            value = Path(help_field_value).absolute()
        assert (
            value == class_default_value
        ), f"Default value from help for '{help_field_name}' is different than decalred in BeekeeperDefaults."
    assert (
        len(default_fields) == 0
    ), f"Not all arguments have be covered, it means that there are different arguments in help : '{default_fields}'"


async def test_config_fields_coverege(tmp_path: Path) -> None:
    """Test will check for the differences between config.ini file and BeekeeperConfig class."""
    # ARRANGE
    tempdir = tmp_path / "test_config_fields_covereg"
    tempdir.mkdir()

    coverege_config_path = tempdir / "config-covereg.ini"
    default_config = Beekeeper().generate_beekeepers_default_config(coverege_config_path)

    with coverege_config_path.open() as config:
        config_class_fields = set(default_config.__fields__.keys())
        in_config_fields = set()

        comment_line_start = "# "
        separator_mark = " = "

        # ACT
        for line in config:
            if (line := line.strip("\n")) and separator_mark in line:
                field_name = (
                    line[2:].split(separator_mark)[0]
                    if line.startswith(comment_line_start)
                    else line.split(separator_mark)[0]
                )
                in_config_fields.add(field_name.replace("-", "_"))

        differences_in_config = in_config_fields - config_class_fields
        differences_in_class = config_class_fields - in_config_fields

        # ASSERT
        for diff_in_config in differences_in_config:
            if diff_in_config in ["rpc_endpoint"]:
                # rpc_endpoint - Local http and websocket endpoint for webserver requests. Deprecated in favor of webserver-http-endpoint and webserver-ws-endpoint
                continue
            pytest.fail(
                f"Field `{diff_in_config}` exists in config.ini file, but does not have representation in"
                " BeekeeperConfig class."
            )

        for diff_in_class in differences_in_class:
            if diff_in_class in ["plugin"]:
                # plugin - Plugin(s) to enable, may be specified multiple times
                continue
            pytest.fail(
                f"Field `{diff_in_class}` exists in BeekeeperConfig class, but does not have representation in"
                " config.ini file."
            )
