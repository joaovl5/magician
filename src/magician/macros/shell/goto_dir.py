from pathlib import Path
from magician.commands.wrapper import WrapperCommand
from magician.macros.base import BaseMacro
from magician.plugins.base import BasePlugin
from settings import AppConfig


class GotoDirectoryMacro(BaseMacro):
    def __init__(
        self, plugin: BasePlugin, app_cfg: AppConfig, dir: Path, **kwargs
    ) -> None:
        super().__init__(plugin, app_cfg, **kwargs)
        self.dir = dir

    def process(self) -> WrapperCommand:
        return WrapperCommand(callable=self.plugin.goto_dir, path=self.dir)
