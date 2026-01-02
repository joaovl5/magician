import os

from pathlib import Path
from typing import List, Optional

from magician.settings import AppConfig

from ..utils.open import open_app
from .base import BasePlugin


class KittyPlugin(BasePlugin):
    def __init__(self, app_cfg: AppConfig, *args, **kwargs) -> None:
        super().__init__(app_cfg, *args, **kwargs)
        self.data_folder = self.app_cfg.data_folder / "kitty/"

        os.makedirs(self.data_folder, exist_ok=True)

    def pre_init(self, *_, **__) -> List[str]:
        return []

    def post_init(self, *_, **__) -> List[str]:
        return []

    def create_pane(self, *, name: Optional[str], **__) -> List[str]:
        return [f"new_tab {name}"]

    def goto_dir(self, *, path: Path, **__) -> List[str]:
        resolved_path = str(path.resolve())
        return [f"cd {resolved_path}"]

    def run_cmd(self, *, command: List[str], **__) -> List[str]:
        joint_cmd = " ".join(command)
        return [f"launch {joint_cmd}"]

    def _get_script_path(self, *, script_name: str) -> Path:
        return self.data_folder / f"{script_name}.conf"

    def write_script(self, *, name: str, contents: List[str], **__) -> None:
        with open(self._get_script_path(script_name=name), "w") as file:
            file.write("\n".join(contents))

    def remove_script(self, *, name: str, **__) -> None:
        script_path = self._get_script_path(script_name=name)
        if not script_path.exists():
            raise Exception(f"Script named {name} doesn't exist.")

        os.remove(self._get_script_path(script_name=name))

    def run_script(self, *, name: str) -> None:
        open_app(self.get_script_cmd(script_name=name))

    def get_script_cmd(self, *, script_name: str, **__) -> List[str]:
        script_path = self._get_script_path(script_name=script_name)
        if not script_path.exists():
            raise Exception(f"Script named {script_name} doesn't exist.")

        return [
            "kitty",
            "--detach",
            "--session",
            f"{script_path.resolve()}",
        ]
