from __future__ import annotations

from clive.__private.ui.clive_screen import clive_on
from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.form_screen import FormScreen, FormScreenBase


class FinishProfileCreationMixin(FormScreenBase[CreateProfileContext]):
    @clive_on(FormScreen.Finish)
    async def finish(self) -> None:
        self._owner.add_post_action(self.app.update_alarms_data_asap_on_newest_node_data)

        profile = self.context.profile
        profile.enable_saving()
        await self.world.switch_profile(profile)

        await self._owner.execute_post_actions()
        await self._handle_modes_on_finish()
        await self.commands.save_profile()

    async def _handle_modes_on_finish(self) -> None:
        await self.app.switch_mode("dashboard")
        await self.app.remove_mode("create_profile")
        await self.app.remove_mode("unlock")
