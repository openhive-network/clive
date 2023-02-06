from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import AnyContainer, Dimension, ScrollablePane
from prompt_toolkit.widgets import Button, Label, TextArea

from clive.ui.component import Component
from clive.ui.table import DoubleBorder, Merge, Table

if TYPE_CHECKING:
    from clive.ui.transfer_to_account.transfer_to_account_view import TransferToAccountView  # noqa: F401


class TransferToAccountPanel(Component["TransferToAccountView"]):
    def __init__(self, parent: TransferToAccountView):
        super().__init__(parent)

    def _create_container(self) -> AnyContainer:
        txt1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut purus nibh, sollicitudin at lorem eget, tristique fringilla purus. Donec sit amet lectus porta, aliquam ligula sed, sagittis eros. Proin in augue leo. Donec vitae erat pellentesque, hendrerit tellus malesuada, mollis urna. Nam varius, lorem id porttitor euismod, erat sapien tempus odio, ac porttitor eros lacus et magna. Nam in arcu pellentesque, bibendum est vel, viverra nulla. Ut ut accumsan risus. Donec at volutpat tortor. Nulla ac elementum lacus. Pellentesque nec nibh tempus, posuere massa nec, consequat lorem. Curabitur ac sollicitudin neque. Donec vel ante magna. Nunc nec sapien vitae sem bibendum volutpat. Donec posuere nulla felis, id mattis risus dictum ut. Fusce libero mi, varius aliquet commodo at, tempus ut eros."
        txt2 = "Praesent eu ultrices massa. Cras et dui bibendum, venenatis urna nec, porttitor sem. Nullam commodo tempor pellentesque. Praesent leo odio, fermentum a ultrices a, ultrices eu nibh. Etiam commodo orci urna, vitae egestas enim ultricies vel. Cras diam eros, rutrum in congue ac, pretium sed quam. Cras commodo ut ipsum ut sollicitudin."
        txt4 = "Morbi viverra, justo eget pretium sollicitudin, magna ex sodales ligula, et convallis erat mauris eu urna. Curabitur tristique quis metus at sodales. Nullam tincidunt convallis lorem in faucibus. Donec nec turpis ante. Ut tincidunt neque eu ornare sagittis. Suspendisse potenti. Etiam tellus est, porttitor eget luctus sed, euismod et erat. Vivamus commodo, massa eget mattis eleifend, turpis sem porttitor dolor, eu finibus ex erat id tellus. Etiam viverra iaculis tellus, ut tempus tellus. Maecenas arcu lectus, euismod accumsan erat eu, blandit vehicula dui. Nulla id ante egestas, imperdiet nibh et, fringilla orci. Donec ut pretium est. Vivamus feugiat facilisis iaculis. Pellentesque imperdiet ex felis, ac elementum dolor tincidunt eget. Cras molestie tellus id massa suscipit, hendrerit vulputate metus tincidunt. Aliquam erat enim, rhoncus in metus eu, consequat cursus ipsum."
        txt6 = "Ut egestas vel nisi et sodales. Etiam arcu massa, viverra in pellentesque quis, molestie a lacus. Nulla suscipit mi luctus blandit dignissim. Proin ac turpis sit amet enim luctus venenatis quis et orci. Donec sed tortor ex. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In et turpis sapien. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vivamus et purus et ex interdum commodo at non velit. Nullam eget diam et felis accumsan gravida non vitae nulla. Morbi tellus mauris, tristique non vulputate eu, efficitur at tellus. Morbi in erat et purus euismod luctus vel vel erat. Fusce auctor augue felis, quis ornare justo mattis vel."
        txt8 = "Donec placerat lacus egestas, aliquam enim vitae, congue ipsum. Praesent vitae eros cursus, pulvinar lectus et, ornare ipsum. Fusce luctus odio vitae hendrerit mollis. Morbi eu turpis vel elit tristique ullamcorper at sodales turpis. Curabitur in ante tincidunt, pellentesque lacus non, dignissim arcu. Mauris ut egestas mi, id elementum ipsum. Morbi justo nisi, laoreet nec lobortis nec, vulputate et justo. Quisque vel pretium quam. Cras consequat quam erat, eu finibus nisi pretium eu. Maecenas ac commodo lacus, non lobortis nunc."
        txt10 = "Aliquam eleifend mi arcu, sit amet convallis tellus condimentum sit amet. Duis lobortis nisl lectus, et convallis augue bibendum sit amet. Maecenas vestibulum porta lorem eu pharetra. Aliquam erat volutpat. Pellentesque volutpat nunc sit amet sem vestibulum commodo. In consequat diam id eros tincidunt dignissim. Maecenas aliquam, elit vitae consectetur facilisis, enim lectus facilisis dui, sed sodales leo dui et augue. Phasellus convallis lacinia pellentesque. Mauris et vulputate ligula. Quisque et velit diam. Pellentesque maximus, augue sit amet semper malesuada, urna velit ultrices lorem, et commodo tortor nibh non justo. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas."

        sht1 = "Hello World"
        sht2 = "Buzz"
        sht3 = "The quick brown fox jumps over the lazy dog."
        table = [
            [TextArea(sht1), Label(txt2), TextArea(txt1)],
            [Merge(TextArea(sht2), 2), TextArea(txt4)],
            [Button(sht3), Merge(TextArea(txt6), 3)],
            [Button(sht1), TextArea(txt8)],
            [TextArea(sht2), TextArea(txt10)],         [Button(sht3), Merge(TextArea(txt6), 3)],
            [Button(sht1), TextArea(txt8)],
            [TextArea(sht2), TextArea(txt10)],         [Button(sht3), Merge(TextArea(txt6), 3)],
            [Button(sht1), TextArea(txt8)],
            [TextArea(sht2), TextArea(txt10)],
        ]

        return ScrollablePane(Table(
            table=table,
            column_width=Dimension.exact(15),
            column_widths=[None],
            borders=DoubleBorder
        ))
