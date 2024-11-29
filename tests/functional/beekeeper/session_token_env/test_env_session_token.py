from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.types import EnvContextFactory


async def test_env_beekeeper_session_token(
    beekeeper: Beekeeper,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
) -> None:
    """Check if beekeeper will use session token provided by CLIVE_BEEKEEPER_SESSION_TOKEN."""
    # ARRANGE
    token = (
        await beekeeper.api.create_session(
            notifications_endpoint=beekeeper.notification_server_http_endpoint.as_string(with_protocol=False),
            salt="salt",
        )
    ).token

    assert token is not None, "There should be new token."
    assert token != beekeeper.token, "New token, should be different than beekeepers current token."

    # ACT & ASSERT
    with beekeeper_session_token_env_context_factory(token):
        assert token == beekeeper.token, "New token should be used by beekeeper."
    assert token != beekeeper.token, "Again, new token, should be different than beekeepers current token."
