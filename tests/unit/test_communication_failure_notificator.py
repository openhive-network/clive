from __future__ import annotations

from typing import Final

import beekeepy.exceptions as bke

from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator

URL: Final[str] = "http://127.0.0.1:8090"


def _create_error(response: dict[str, object] | None) -> bke.CommunicationError:
    return bke.CommunicationError(URL, request=b"{}", response=response)


def test_error_message_is_preferred_when_data_is_exception_of_service() -> None:
    # ARRANGE
    message = "Assert Exception:false: Account alice does not have sufficient funds for transfer."
    error = _create_error(
        {"error": {"code": -32003, "message": message, "data": {"code": 10, "name": "assert_exception", "stack": []}}}
    )

    # ACT
    messages = CommunicationFailureNotificator._get_error_messages(error)

    # ASSERT
    assert messages == [message]


def test_error_data_is_used_when_it_is_text() -> None:
    # ARRANGE
    data = "Wallet not found: alice"
    error = _create_error({"error": {"code": -32000, "message": "Internal Error", "data": data}})

    # ACT
    messages = CommunicationFailureNotificator._get_error_messages(error)

    # ASSERT
    assert messages == [data]


def test_error_messages_are_empty_without_response() -> None:
    # ARRANGE
    error = _create_error(None)

    # ACT
    messages = CommunicationFailureNotificator._get_error_messages(error)

    # ASSERT
    assert messages == []
