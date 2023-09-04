from __future__ import annotations

from typing import Any


def get_proto_operation_name(operation: dict[str, Any]) -> str:
    """
    Get the name of the operation from the operation dict.

    Example:
    -------
    operation = {
        "comment": {
            "parent_permlink": "/",
            "author": "alice",
            "permlink": "/",
            "title": "Best comment",
            "body": "<span>comment</span>",
            "json_metadata": "{}"
        }
    }

    get_proto_operation_name(operation) -> "comment"
    """
    return next(iter(operation))
