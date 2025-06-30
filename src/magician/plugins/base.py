from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional
import attrs

from magician.settings import AppConfig


class PluginLevel(Enum):
    ROOT = auto()  # can be root and child
    CHILD = auto()  # cannot be root


@attrs.define
class PluginInfo:
    plugin_level: PluginLevel


class BasePlugin(ABC):
    def __init__(self, app_cfg: AppConfig, *args, **kwargs) -> None:
        self.app_cfg = app_cfg

    # methods for generating scripts, returning lists of plugin-specific commands

    # in case any special commands are needed before and/or after initialization
    @abstractmethod
    def pre_init(self, *_, **__) -> List[str]: ...

    @abstractmethod
    def post_init(self, *_, **__) -> List[str]: ...

    @abstractmethod
    def create_pane(self, *, name: Optional[str], **__) -> List[str]: ...

    @abstractmethod
    def goto_dir(self, *, path: Path, **__) -> List[str]: ...

    @abstractmethod
    def run_cmd(self, *, command: List[str], **__) -> List[str]: ...

    # methods for managing scripts

    @abstractmethod
    def write_script(self, *, name: str, contents: List[str], **__) -> None: ...

    @abstractmethod
    def run_script(self, *, name: str) -> None: ...

    @abstractmethod
    def remove_script(self, *, name: str) -> None: ...

    @abstractmethod
    def get_script_cmd(self, *, script_name: str, **__) -> List[str]:
        """
        Returns (shell) command(s) required for executing plugin script
        """
