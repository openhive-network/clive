from __future__ import annotations

from abc import ABC

from clive.ui.component import Component, ConfigurableComponent
from clive.ui.parented import Parented
from clive.ui.view_manager_base import ViewManagerBase

class View(Parented[ViewManagerBase], ABC):
    """
    A view is a kind of component that consists of other components and determines their final layout/arrangement.
    It should not be part of another view or component. Specifies the final appearance that can be shown to the user.
    """

class ReadyView(Component[ViewManagerBase], View, ABC):
    """
    This View is not required to configure, after constructor
    it's ready to use
    """

class ConfigurableView(ConfigurableComponent[ViewManagerBase], View, ABC):
    """
    This View is not ready after construction it is required to
    use with statement to finish setting this class, example:

    with SomeConfigurableView(parent=self, arg1=value1) as view:
        view.main_panel = MainPanel(parent=view)
        view.side_panel = SidePanel(parent=view, arg2=value2)
        for i in range(10):
            view.main_panel.add_checkbox(f'Some label no. {i}')

    After exiting with statement element is ready to go
    """
