from __future__ import annotations

import warnings

from hiveio_api import MissingFieldWarning, UnexpectedFieldWarning


def _disable_schemas_extra_fields_check() -> None:
    """Accept fields of responses not declared in models of hiveio_api and fields missing in responses of get_config."""
    warnings.filterwarnings("ignore", category=UnexpectedFieldWarning)
    warnings.filterwarnings("ignore", message=r"GetConfigResponse: ", category=MissingFieldWarning)


# This has to be executed before any API call
# Otherwise warnings about fields of responses will be shown
_disable_schemas_extra_fields_check()
