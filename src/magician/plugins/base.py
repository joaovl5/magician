from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional
import attrs


class PluginLevel(Enum):
    ROOT = auto()  # can be root and child
    CHILD = auto()  # cannot be root


@attrs.define
class PluginInfo:
    plugin_level: PluginLevel


class BasePlugin(ABC):
    # methods for generating scripts, returning lists of plugin-specific commands

    @abstractmethod
    def create_pane(self, *, name: Optional[str], **kwargs) -> List[str]: ...

    @abstractmethod
    def goto_dir(self, *, path: Path, **kwargs) -> List[str]: ...

    @abstractmethod
    def run_cmd(self, *, command: List[str], **kwargs) -> List[str]: ...

    # methods for managing scripts

    @abstractmethod
    def write_script(self, *, name: str, contents: List[str], **kwargs) -> None: ...

    @abstractmethod
    def run_script(self, *, name: str) -> None: ...

    @abstractmethod
    def remove_script(self, *, name: str) -> None: ...

    @abstractmethod
    def get_script_cmd(self, *, script_name: str, **kwargs) -> List[str]:
        """
        Returns (shell) command(s) required for executing plugin script
        """
