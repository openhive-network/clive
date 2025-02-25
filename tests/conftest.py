from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.before_launch import (
    _create_clive_data_directory,
    _disable_schemas_extra_fields_check,
    _initialize_user_settings,
)
from clive.__private.core._thread import thread_pool
from clive.__private.core.constants.setting_identifiers import DATA_PATH, LOG_LEVEL_1ST_PARTY, LOG_LEVELS, LOG_PATH
from clive.__private.logger import logger
from clive.__private.settings import safe_settings, settings
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    NODE_CHAIN_ID_ENV_NAME,
    SECRETS_NODE_ADDRESS_ENV_NAME,
    TESTNET_CHAIN_ID,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive_local_tools.types import EnvContextFactory, GenericEnvContextFactory


@pytest.fixture(autouse=True, scope="session")
def manage_thread_pool() -> Iterator[None]:
    with thread_pool:
        yield


def _prepare_settings() -> None:
    settings.reload()

    working_directory = tt.context.get_current_directory() / "clive"
    settings.set(DATA_PATH, working_directory)

    _create_clive_data_directory()
    _initialize_user_settings()

    beekeeper_directory = working_directory / "beekeeper"
    if beekeeper_directory.exists():
        shutil.rmtree(beekeeper_directory)

    profile_data_directory = working_directory / "data"
    if profile_data_directory.exists():
        shutil.rmtree(profile_data_directory)

    settings.set(LOG_PATH, working_directory / "logs")

    settings.set(LOG_LEVELS, ["DEBUG"])
    settings.set(LOG_LEVEL_1ST_PARTY, "DEBUG")

    safe_settings.validate()


@pytest.fixture
def testnet_chain_id_env_context(generic_env_context_factory: GenericEnvContextFactory) -> Generator[None]:
    chain_id_env_context_factory = generic_env_context_factory(NODE_CHAIN_ID_ENV_NAME)
    with chain_id_env_context_factory(TESTNET_CHAIN_ID):
        yield


@pytest.fixture
def logger_configuration_factory() -> Callable[[], None]:
    def _logger_configuration_factory() -> None:
        logger.setup(enable_textual=False, enable_stream_handlers=True)

    return _logger_configuration_factory


@pytest.fixture(autouse=True)
def prepare_before_launch(
    testnet_chain_id_env_context: None,  # noqa: ARG001
    logger_configuration_factory: Callable[[], None],
) -> None:
    _prepare_settings()
    _disable_schemas_extra_fields_check()
    logger_configuration_factory()


@pytest.fixture
def generic_env_context_factory(monkeypatch: pytest.MonkeyPatch) -> GenericEnvContextFactory:
    def factory(env_name: str) -> EnvContextFactory:
        def _setdelenv(value: str | None) -> None:
            monkeypatch.setenv(env_name, value) if value else monkeypatch.delenv(env_name, raising=False)
            settings.reload()

        @wraps(factory)
        @contextmanager
        def impl(value: str | None) -> Generator[None]:
            previous_value = os.getenv(env_name)
            _setdelenv(value)
            yield
            _setdelenv(previous_value)

        return impl

    return factory


@pytest.fixture
def beekeeper_remote_address_env_context_factory(
    generic_env_context_factory: GenericEnvContextFactory,
) -> EnvContextFactory:
    return generic_env_context_factory(BEEKEEPER_REMOTE_ADDRESS_ENV_NAME)


@pytest.fixture
def beekeeper_session_token_env_context_factory(
    generic_env_context_factory: GenericEnvContextFactory,
) -> EnvContextFactory:
    return generic_env_context_factory(BEEKEEPER_SESSION_TOKEN_ENV_NAME)


@pytest.fixture
def node_address_env_context_factory(generic_env_context_factory: GenericEnvContextFactory) -> EnvContextFactory:
    return generic_env_context_factory(SECRETS_NODE_ADDRESS_ENV_NAME)
