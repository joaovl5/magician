from pathlib import Path
import shlex
from typing import Dict, List, Optional, Tuple, Type

from loguru import logger
from magician.commands.base import BaseCommand
from magician.commands.shell import ShellCommand, ShellCommandOptions
from magician.config.schema import (
    MacroCommand,
    MagicConfigSchema,
    ProjectConfig,
    RunCommand,
    WizardBackendConfig,
    WizardBackendType,
    WizardConfig,
)
from magician.macros.base import BaseMacro
from magician.macros.mapping import MACRO_MAPPINGS
from magician.macros.plugins.create_pane import CreatePaneMacro
from magician.macros.shell.goto_dir import GotoDirectoryMacro
from magician.plugins.base import BasePlugin
from magician.plugins.kitty import KittyPlugin
from magician.plugins.tmux import TmuxPlugin
from magician.settings import AppConfig
import functools

ROOT_PLUGINS = {
    WizardBackendType.KITTY,
}

PLUGIN_BACKEND_MAP: Dict[WizardBackendType, Type[BasePlugin]] = {
    WizardBackendType.KITTY: KittyPlugin,
    WizardBackendType.TMUX: TmuxPlugin,
}


class InterpreterException(Exception): ...


class NotFoundException(InterpreterException): ...


class ConfigInterpreter:
    def __init__(self, app_cfg: AppConfig) -> None:
        self.app_cfg = app_cfg

        # maybe will turn into a property later
        self.shell_cmd_opts = ShellCommandOptions()

    def _read_backend(
        self, backend: WizardBackendType | WizardBackendConfig
    ) -> WizardBackendConfig:
        if isinstance(backend, WizardBackendConfig):
            return backend
        else:
            return WizardBackendConfig(name=backend, options={})

    def setup_plugins(
        self, config: WizardConfig
    ) -> Tuple[BasePlugin, Optional[BasePlugin]]:
        root_backend = self._read_backend(backend=config.root.backend)

        if root_backend.name not in ROOT_PLUGINS:
            raise NotImplementedError(
                f"Backend type '{root_backend.name.value}' not supported as a root plugin."
            )

        root_backend_plugin_cls = PLUGIN_BACKEND_MAP[root_backend.name]
        root_backend_plugin = root_backend_plugin_cls(
            app_cfg=self.app_cfg,
            **root_backend.options,
        )

        if not config.root.nested:
            return (root_backend_plugin, None)

        nested_backend = self._read_backend(backend=config.root.nested.backend)

        nested_backend_cls = PLUGIN_BACKEND_MAP[nested_backend.name]
        nested_backend_plugin = nested_backend_cls(
            app_cfg=self.app_cfg,
            **nested_backend.options,
        )

        return (root_backend_plugin, nested_backend_plugin)

    def gather_raw_commands(
        self,
        cmd_data: List[RunCommand],
        plugin: BasePlugin,
    ) -> List[BaseCommand | BaseMacro]:
        raw_cmds = []
        for cmd in cmd_data:
            if isinstance(cmd, MacroCommand):
                macro_cls = MACRO_MAPPINGS.get(cmd.macro)
                if not macro_cls:
                    raise NotFoundException(
                        f"Macro named '{cmd.macro}' does not exist."
                    )
                macro = macro_cls(plugin=plugin, app_cfg=self.app_cfg, **cmd.options)
                raw_cmds.append(macro)
            else:
                # string commands become shell commands
                shell_cmd = ShellCommand(
                    plugin=plugin, cmd=cmd, opts=self.shell_cmd_opts
                )
                raw_cmds.append(shell_cmd)
        return raw_cmds

    def process_raw_commands(
        self, raw_cmds: List[BaseCommand | BaseMacro]
    ) -> List[BaseCommand]:
        processed_cmds = []
        for raw_cmd in raw_cmds:
            if isinstance(raw_cmd, BaseMacro):
                cmd = raw_cmd.process()
                processed_cmds.append(cmd)
            else:
                processed_cmds.append(raw_cmd)
        return processed_cmds

    def compile(self, config: MagicConfigSchema, schema_name: str) -> None:
        root_plugin, nested_plugin = self.setup_plugins(config=config.wizard)
        logger.trace("Starting config compilation")
        logger.trace(
            f"Root plugin: {root_plugin.__class__.__name__}, Nested plugin: {nested_plugin.__class__.__name__}"
        )

        project = config.project
        project_dir = project.dir  # base dir will serve as root of project

        root_script_cmds = []
        root_script_cmds.extend(root_plugin.pre_init())
        for root_pane_name, root_pane_data in project.setup.items():
            raw_root_cmds: List[BaseCommand | BaseMacro] = []
            raw_root_cmds.append(
                CreatePaneMacro(
                    app_cfg=self.app_cfg,
                    plugin=root_plugin,
                    name=root_pane_name,
                )
            )

            # goto dir command if project and/or pane have "dir" attributes
            root_pane_dir: Optional[Path] = None
            if project_dir:
                root_pane_dir = project_dir
            if root_pane_data.dir:
                root_pane_dir = (
                    root_pane_dir / root_pane_data.dir
                    if root_pane_dir
                    else root_pane_data.dir
                )
            if root_pane_dir:
                raw_root_cmds.append(
                    GotoDirectoryMacro(
                        plugin=root_plugin, app_cfg=self.app_cfg, dir=root_pane_dir
                    )
                )

            if root_pane_data.run_before:
                raise InterpreterException("Root pane CANNOT have 'run-before' set.")

            root_run_cmds_factory = functools.partial(
                self.gather_raw_commands, cmd_data=root_pane_data.run
            )

            if not root_pane_data.nested:
                # prepare commands right away and continue to next pane
                root_run_cmds = root_run_cmds_factory(plugin=root_plugin)
                raw_root_cmds.extend(root_run_cmds)
                root_cmds = self.process_raw_commands(raw_cmds=raw_root_cmds)
                for cmd in root_cmds:
                    root_script_cmds.extend(cmd.run())
                continue
            if not nested_plugin:
                raise InterpreterException(
                    "Must have a nested backend for a root pane with nested=true"
                )
            if not root_pane_data.panes:
                raise InterpreterException(
                    "Root pane with nested=true must have at least 1 child pane."
                )

            # if nested, handle nested script

            child_script_cmds = []
            child_script_cmds.extend(nested_plugin.pre_init())
            for child_pane_name, child_pane_data in root_pane_data.panes.items():
                raw_child_cmds: List[BaseCommand | BaseMacro] = []
                raw_child_cmds.append(
                    CreatePaneMacro(
                        app_cfg=self.app_cfg,
                        plugin=nested_plugin,
                        name=child_pane_name,
                    )
                )

                child_pane_dir: Optional[Path] = None
                if root_pane_dir:
                    child_pane_dir = root_pane_dir
                if child_pane_data.dir:
                    child_pane_dir = (
                        child_pane_dir / child_pane_data.dir
                        if child_pane_dir
                        else child_pane_data.dir
                    )
                if child_pane_dir:
                    raw_child_cmds.append(
                        GotoDirectoryMacro(
                            plugin=nested_plugin,
                            app_cfg=self.app_cfg,
                            dir=child_pane_dir,
                        )
                    )

                child_run_before_cmds = self.gather_raw_commands(
                    cmd_data=child_pane_data.run_before,
                    plugin=nested_plugin,
                )
                child_run_cmds = self.gather_raw_commands(
                    cmd_data=child_pane_data.run,
                    plugin=nested_plugin,
                )

                # run-before cmd set goes BEFORE parent commands
                # then parent's
                # then child's run cmds.
                root_run_cmds = root_run_cmds_factory(plugin=nested_plugin)
                computed_run_cmds = [
                    *child_run_before_cmds,
                    *root_run_cmds,
                    *child_run_cmds,
                ]

                raw_child_cmds.extend(computed_run_cmds)
                child_cmds = self.process_raw_commands(raw_cmds=raw_child_cmds)

                for cmd in child_cmds:
                    # we're ASSUMING all cmds so far return List[str] when run
                    child_script_cmds.extend(cmd.run())

            child_script_cmds.extend(nested_plugin.post_init())

            child_script_name = f"{schema_name}_{root_pane_name}"
            nested_plugin.write_script(
                name=child_script_name, contents=child_script_cmds
            )

            run_child_script_cmd = ShellCommand(
                plugin=root_plugin,  # root plugin will be calling the script
                cmd=nested_plugin.get_script_cmd(script_name=child_script_name),
                opts=self.shell_cmd_opts,
            )

            raw_root_cmds.append(run_child_script_cmd)
            root_cmds = self.process_raw_commands(raw_cmds=raw_root_cmds)

            for cmd in root_cmds:
                root_script_cmds.extend(cmd.run())

        root_script_cmds.extend(root_plugin.post_init())

        root_script_name = f"{schema_name}"
        root_plugin.write_script(name=root_script_name, contents=root_script_cmds)

    def run(self, config: MagicConfigSchema, schema_name: str) -> None:
        root_plugin, _ = self.setup_plugins(config=config.wizard)
        root_plugin.run_script(name=schema_name)
