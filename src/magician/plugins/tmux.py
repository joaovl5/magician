import os
import shlex
from pathlib import Path
from typing import List, Optional

import attrs

from magician.utils.ensure_executable import ensure_executable
from magician.settings import AppConfig

from ..utils.open import open_app
from .base import BasePlugin

from uuid import uuid4


@attrs.define
class TmuxProjectConfig:
    start_count_at_one: bool = False


class TmuxPlugin(BasePlugin):
    def __init__(self, app_cfg: AppConfig, *args, **kwargs) -> None:
        super().__init__(app_cfg, *args, **kwargs)
        self.tmux_cfg = TmuxProjectConfig(*args, **kwargs)
        self.data_folder = app_cfg.data_folder / "tmux/"
        self._window_current_index = -1

        os.makedirs(self.data_folder, exist_ok=True)

    @property
    def window_current_index(self):
        increment = 1 if self.tmux_cfg.start_count_at_one else 0
        return self._window_current_index + increment

    def window_increment_index(self) -> int:
        self._window_current_index += 1
        return self.window_current_index

    def pre_init(self, *_, session_name: Optional[str] = None, **__) -> List[str]:
        # reset index for preparing a new script
        self._window_current_index = -1
        self._session_name = session_name or uuid4().hex

        return [
            f"SESSION_NAME={self._session_name}",
            'if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then',
            '   tmux attach-session -t "$SESSION_NAME"',
            "   exit 0",
            "fi",
            'tmux new-session -d -s "$SESSION_NAME"',
        ]

    def post_init(self, *_, **__) -> List[str]:
        return ['tmux attach-session -t "$SESSION_NAME"']

    def create_pane(self, *, name: Optional[str], **__) -> List[str]:
        safe_name: Optional[str] = shlex.quote(name) if name else None

        return [
            f"tmux new-window -t {self._session_name}:{self.window_increment_index()} -k"
            + (f" -n {safe_name}" if safe_name else ""),
        ]

    def goto_dir(self, *, path: Path, resolve: bool = False, **__) -> List[str]:
        if resolve:
            path = path.resolve()
        safe_path = shlex.quote(f"cd {path}")
        return [
            f'tmux send-keys -t "$SESSION_NAME":{self.window_current_index} {safe_path} C-m'
        ]

    def run_cmd(self, *, command: List[str], **__) -> List[str]:
        safe_cmd = shlex.quote(shlex.join(command))
        return [
            f'tmux send-keys -t "$SESSION_NAME":{self.window_current_index} {safe_cmd} C-m'
        ]

    def _get_script_path(self, *, script_name: str) -> Path:
        return self.data_folder / f"{script_name}.sh"

    def write_script(self, *, name: str, contents: List[str], **__) -> None:
        path = self._get_script_path(script_name=name)
        with open(path, "w") as file:
            file.write("\n".join(contents))
        ensure_executable(path=path)

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

        return ["bash", "-c", f"'{script_path.resolve()}'"]
