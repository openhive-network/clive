from __future__ import annotations

from clive.__private.models.schemas import ExtraFieldsPolicy, MissingFieldsInGetConfigPolicy, set_policies


def _disable_schemas_extra_fields_check() -> None:
    set_policies(ExtraFieldsPolicy(allow=True), MissingFieldsInGetConfigPolicy(allow=True))


# This has to be executed before any import that loads schemas
# Otherwise policy won't be used
_disable_schemas_extra_fields_check()
