from __future__ import annotations

from typing import Final

import pytest
from helpy.exceptions import CommunicationError

from clive.__private.core.suppress_not_existing_apis import SuppressNotExistingApis

URL: Final[str] = "http://doesnt_matter.com"
REQUEST: Final[str] = "doesnt_matter"


def create_error_response(api_name: str) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "message": f"Assert Exception:api_itr != data._registered_apis.end(): Could not find API {api_name}",
        }
    }


def test_suppressing_single_api() -> None:
    # ARRANGE
    response = str(create_error_response("rc_api"))

    # ACT & ASSERT
    with SuppressNotExistingApis("rc_api"):
        raise CommunicationError(URL, REQUEST, response=response)


def test_suppressing_multiple_apis() -> None:
    # ARRANGE
    response = str([create_error_response("rc_api"), create_error_response("reputation_api")])

    # ACT & ASSERT
    with SuppressNotExistingApis("rc_api", "reputation_api", "not_existing_api"):
        raise CommunicationError(URL, REQUEST, response=response)


def test_raising_exception_when_api_is_not_suppressed() -> None:
    # ARRANGE
    response = str([create_error_response("rc_api"), create_error_response("reputation_api")])

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match="Could not find API reputation_api"):  # noqa: SIM117
        with SuppressNotExistingApis("rc_api"):
            raise CommunicationError(URL, REQUEST, response=response)
