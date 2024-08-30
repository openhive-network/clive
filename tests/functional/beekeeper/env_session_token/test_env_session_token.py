from __future__ import annotations

import os
from typing import TYPE_CHECKING

from clive.__private.core.constants.setting_identifiers import BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar, settings

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


async def test_env_beekeeper_session_token(beekeeper: Beekeeper) -> None:
    """Check if beekeeper will use session token provided by CLIVE_BEEKEEPER_SESSION_TOKEN."""
    # ARRANGE
    env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
    token = (
        await beekeeper.api.create_session(
            notifications_endpoint=beekeeper.notification_server_http_endpoint.as_string(with_protocol=False),
            salt="salt",
        )
    ).token

    assert token is not None, "There should be new token."
    assert token != beekeeper.token, "New token, should be different than beekeepers current token."

    # ACT & ASSERT
    os.environ[env_var] = token
    settings.reload()
    assert token == beekeeper.token, "New token should be used by beekeeper."

    del os.environ[env_var]
    settings.reload()
    assert token != beekeeper.token, "Again, new token, should be different than beekeepers current token."
