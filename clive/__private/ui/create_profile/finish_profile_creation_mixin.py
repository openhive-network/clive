from __future__ import annotations

from textual import on

from clive.__private.ui.create_profile.context import CreateProfileContext
from clive.__private.ui.create_profile.form_screen import FormScreen, FormScreenBase


class FinishProfileCreationMixin(FormScreenBase[CreateProfileContext]):
    @on(FormScreen.Finish)
    async def finish(self) -> None:
        # Has to be done in a separate task to avoid deadlock. More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker(self._finish())

    async def _finish(self) -> None:
        self._owner.add_post_action(self.app.update_alarms_data_asap_on_newest_node_data)

        profile = self.context.profile
        profile.enable_saving()
        self.world.profile = profile

        await self._owner.execute_post_actions()
        await self._handle_modes_on_finish()
        self.profile.save()

    async def _handle_modes_on_finish(self) -> None:
        await self.app.switch_mode("dashboard")
        await self.app.remove_mode("create_profile")
        await self.app.remove_mode("unlock")
