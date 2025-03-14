from __future__ import annotations

from textual import on

from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.form_screen import FormScreen, FormScreenBase


class FinishProfileCreationMixin(FormScreenBase[CreateProfileContext]):
    @on(FormScreen.Finish)
    async def finish(self) -> None:
        # Has to be done in a separate task to avoid deadlock. More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker(self._finish())

    async def _finish(self) -> None:
        self._owner.add_post_action(
            lambda: self.app.update_alarms_data_on_newest_node_data(suppress_cancelled_error=True),
            self.app.resume_refresh_alarms_data_interval,
        )

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
