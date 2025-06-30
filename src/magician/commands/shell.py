import shlex
from typing import List, Optional, Tuple

import attrs

from magician.config.schema import WizardBackendType
from magician.plugins.base import BasePlugin
from .base import BaseCommand


@attrs.define
class ShellCommandOptions:
    prefix: List[str] = []
    suffix: List[str] = []


class ShellCommand(BaseCommand):
    BACKEND_AGNOSTIC: bool = False
    SUPPORTED_BACKENDS: Tuple[WizardBackendType, ...] = (
        WizardBackendType.KITTY,
        WizardBackendType.TMUX,
    )

    def __init__(
        self,
        *,
        plugin: BasePlugin,
        cmd: str | List[str],
        opts: Optional[ShellCommandOptions] = None,
        **_,
    ) -> None:
        super().__init__()

        if not opts:
            opts = ShellCommandOptions()
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        self.opts = opts
        self.cmd = cmd
        self.plugin = plugin

    def run(self, **_) -> List[str]:
        return self.plugin.run_cmd(
            command=[*self.opts.prefix, *self.cmd, *self.opts.suffix]
        )
