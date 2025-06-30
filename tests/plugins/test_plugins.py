from pathlib import Path
from typing import List, Type

from magician.plugins.base import BasePlugin
from magician.plugins.kitty import KittyPlugin
from magician.plugins.tmux import TmuxPlugin, TmuxProjectConfig
from magician.settings import AppConfig

import pytest


def base_plugin_asserts(
    plugin: BasePlugin,
    run=True,
    custom_cmds: List[List[str]] = [],
    remove_after=True,
):
    create_pane_cmd = plugin.create_pane(name="test_pane")
    goto_dir_cmd = plugin.goto_dir(path=Path.home())
    run_cmd_cmd = plugin.run_cmd(command=["echo", "Hello"])
    custom_cmds_cmd = []
    for c in custom_cmds:
        custom_cmds_cmd.extend(plugin.run_cmd(command=c))

    joint_cmds = [
        *plugin.pre_init(),
        *create_pane_cmd,
        *goto_dir_cmd,
        *run_cmd_cmd,
        *custom_cmds_cmd,
        *plugin.post_init(),
    ]

    plugin.write_script(name="test_script", contents=joint_cmds)
    if run:
        plugin.run_script(name="test_script")
    if remove_after:
        plugin.remove_script(name="test_script")

    with pytest.raises(Exception):
        assert plugin.run_script(name="non_existent_script")


@pytest.fixture(scope="module")
def kitty_plugin(app_config: AppConfig):
    return KittyPlugin(app_cfg=app_config)


def test_kitty_plugin(kitty_plugin: KittyPlugin):
    base_plugin_asserts(plugin=kitty_plugin)


def test_tmux_plugin(app_config: AppConfig, kitty_plugin: KittyPlugin):
    tmux = TmuxPlugin(
        app_cfg=app_config,
        session_name="test_session",
        start_count_at_one=True,
    )

    base_plugin_asserts(
        plugin=tmux,
        run=False,
        remove_after=False,
        custom_cmds=[
            ["bash"],
        ],
    )

    run_cmd = tmux.get_script_cmd(script_name="test_script")

    kitty_script = [
        *kitty_plugin.pre_init(),
        *kitty_plugin.create_pane(name="test_pane"),
        *kitty_plugin.run_cmd(command=run_cmd),
        *kitty_plugin.create_pane(name="test_pane_2"),
        *kitty_plugin.run_cmd(command=["bash"]),
        *kitty_plugin.post_init(),
    ]

    kitty_plugin.write_script(name="test_script_tmux", contents=kitty_script)
    kitty_plugin.run_script(name="test_script_tmux")

    # kitty_plugin.remove_script(name="test_script_tmux")
    # tmux.remove_script(name="test_script")
