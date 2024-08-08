from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable

from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData
    from clive.__private.storage.accounts import TrackedAccount


class AlarmDisplay(DynamicLabel):
    DEFAULT_CSS = """
    AlarmDisplay {
        text-style: bold;
        background: $error-lighten-3;
        padding: 0 1;
        color: $text;

        &.-no-alarm {
            background: $success-lighten-3;
        }
    }
    """

    def __init__(
        self,
        account_getter: Callable[[ProfileData], Iterable[TrackedAccount]],
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        def update_callback(pd: ProfileData) -> str:
            class_name = "-no-alarm"
            no_alarms_info = "No alarms"
            alarm_count = sum([len(acc.alarms.harmful_alarms) for acc in account_getter(pd)])
            if alarm_count:
                self.remove_class(class_name)
                return f"{alarm_count} ALARM{'S' if alarm_count > 1 else ''}"
            self.add_class(class_name)
            return no_alarms_info

        super().__init__(
            self.world,
            "profile_data",
            update_callback,
            first_try_callback=lambda profile_data: all(
                acc.is_alarms_data_available for acc in account_getter(profile_data)
            ),
            id_=id_,
            classes=classes,
        )
