import os
from pathlib import Path
import shutil
from typing import List, Optional

from settings import AppConfig
from .base import BasePlugin
from ..utils.open import open_app


class KittyPlugin(BasePlugin):
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.data_folder = cfg.data_folder / "kitty/"

        os.makedirs(self.data_folder, exist_ok=True)

    def create_pane(self, *, name: Optional[str], **kwargs) -> List[str]:
        return [f"new_tab {name}"]

    def goto_dir(self, *, path: Path, **kwargs) -> List[str]:
        resolved_path = str(path.resolve())
        return [f"cd {resolved_path}"]

    def run_cmd(self, *, command: List[str], **kwargs) -> List[str]:
        return [f"launch {' '.join(command)}"]

    def _get_script_path(self, *, script_name: str) -> Path:
        return self.data_folder / f"{script_name}.cfg"

    def write_script(self, *, name: str, contents: List[str], **kwargs) -> None:
        with open(self._get_script_path(script_name=name), "w") as file:
            file.write("\n".join(contents))

    def remove_script(self, *, name: str, **kwargs) -> None:
        script_path = self._get_script_path(script_name=name)
        if not script_path.exists():
            raise Exception(f"Script named {name} doesn't exist.")

        os.remove(self._get_script_path(script_name=name))

    def run_script(self, *, name: str) -> None:
        open_app(self.get_script_cmd(script_name=name))

    def get_script_cmd(self, *, script_name: str, **kwargs) -> List[str]:
        script_path = self._get_script_path(script_name=script_name)
        if not script_path.exists():
            raise Exception(f"Script named {script_name} doesn't exist.")

        return [
            "kitty",
            "--session",
            f"{script_path.resolve()}",
        ]
