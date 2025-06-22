from pathlib import Path
from typing import Type

from magician.plugins.base import BasePlugin
from magician.plugins.kitty import KittyPlugin
from settings import AppConfig

import pytest


def base_plugin_asserts(plugin: BasePlugin):
    create_pane_cmd = plugin.create_pane(name="test_pane")
    goto_dir_cmd = plugin.goto_dir(path=Path("~"))
    run_cmd_cmd = plugin.run_cmd(command=["echo", "'Hello'"])

    joint_cmds = [
        *create_pane_cmd,
        *goto_dir_cmd,
        *run_cmd_cmd,
    ]

    plugin.write_script(name="test_script", contents=joint_cmds)
    plugin.run_script(name="test_script")
    plugin.remove_script(name="test_script")

    with pytest.raises(Exception):
        assert plugin.run_script(name="non_existent_script")


def test_kitty_plugin():
    test_cfg = AppConfig.model_validate(
        {
            "data_folder": Path("./test_data/"),
        },
    )

    kitty_plugin = KittyPlugin(cfg=test_cfg)

    base_plugin_asserts(plugin=kitty_plugin)
