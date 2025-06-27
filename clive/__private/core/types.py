from __future__ import annotations

from typing import Literal

MigrationStatus = Literal["migrated", "already_newest"]
NotifyLevel = Literal["info", "warning", "error"]
