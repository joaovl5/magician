from typing import Optional
from magician.commands.wrapper import WrapperCommand
from magician.macros.base import BaseMacro
from magician.plugins.base import BasePlugin
from magician.settings import AppConfig


class CreatePaneMacro(BaseMacro):
    def __init__(
        self,
        app_cfg: AppConfig,
        plugin: BasePlugin,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(plugin, app_cfg, **kwargs)
        self.plugin = plugin
        self.name = name

    def process(self) -> WrapperCommand:
        return WrapperCommand(
            callable=self.plugin.create_pane,
            name=self.name,
        )
