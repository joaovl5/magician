from abc import ABC, abstractmethod

from magician.commands.base import BaseCommand
from magician.plugins.base import BasePlugin
from settings import AppConfig


class BaseMacro(ABC):
    def __init__(self, plugin: BasePlugin, app_cfg: AppConfig, **kwargs) -> None:
        self.plugin = plugin
        self.app_cfg = app_cfg

    @abstractmethod
    def process(self) -> BaseCommand: ...
