from __future__ import annotations

from typing import Literal

SocialAction = Literal["follow", "unfollow", "mute", "unmute"]


def social_action_validates_bad_account(action: SocialAction) -> bool:
    """Return True if this action should block bad accounts."""
    return action != "mute"
