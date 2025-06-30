from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class MacroCommand(BaseModel):
    macro: str = Field(min_length=1)
    options: Dict[str, Any] = Field(default_factory=dict)


RunCommand = str | MacroCommand


class PaneEntry(BaseModel):
    dir: Optional[Path] = None
    run: List[RunCommand] = Field(default_factory=list)
    run_before: List[RunCommand] = Field(default_factory=list, alias="run-before")


class RootPaneEntry(PaneEntry):
    nested: bool = False
    run: List[RunCommand] = Field(default_factory=list)
    panes: Optional[Dict[str, PaneEntry]] = None


class ProjectConfig(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    dir: Optional[Path] = None
    setup: Dict[str, RootPaneEntry] = Field(min_length=1)


class WizardBackendType(Enum):
    KITTY = "kitty"
    TMUX = "tmux"


class WizardBackendConfig(BaseModel):
    name: WizardBackendType
    options: Dict[str, Any] = Field(default_factory=dict)


class WizardMode(Enum):
    TABBED = "tabbed"


class PaneConfig(BaseModel):
    backend: WizardBackendType | WizardBackendConfig
    mode: WizardMode


class RootPaneConfig(PaneConfig):
    nested: Optional[PaneConfig] = None


class WizardConfig(BaseModel):
    root: RootPaneConfig


class MagicConfigSchema(BaseSettings):
    wizard: WizardConfig
    project: ProjectConfig

    @classmethod
    def settings_customise_sources(
        cls, *args, **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        raise Exception("This class is not meant to be directly initialized.")
