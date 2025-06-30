from pathlib import Path
from typing import Optional

from loguru import logger

from magician.commands.shell import ShellCommand
from magician.plugins.base import BasePlugin
from magician.settings import AppConfig, ShellType

from ..base import BaseMacro


class PythonActivateVenvMacro(BaseMacro):
    def __init__(
        self,
        plugin: BasePlugin,
        app_cfg: AppConfig,
        cwd: Optional[Path] = None,
        shell: Optional[ShellType] = None,
        **kwargs,
    ) -> None:
        super().__init__(plugin, app_cfg, **kwargs)
        self.cwd = cwd or Path()
        if not shell:
            shell = app_cfg.default_shell
            logger.trace(f"Using default shell {shell} for activate-venv macro.")
        else:
            logger.trace(f"Using provided shell {shell} for activate-venv macro.")

        self.shell = shell or self.app_cfg.default_shell
        self.plugin = plugin

    @property
    def script_extension(self) -> str:
        match self.shell:
            case ShellType.BASH | ShellType.ZSH:
                return "sh"
            case ShellType.FISH:
                return "fish"
            case _:
                raise NotImplementedError(
                    f"Shell type {self.shell} is not supported for macro."
                )

    def process(self) -> ShellCommand:
        file = self.cwd / ".venv" / "bin" / f"activate.{self.script_extension}"
        resolved_file = str(file)

        return ShellCommand(plugin=self.plugin, cmd=f"source {resolved_file}")
