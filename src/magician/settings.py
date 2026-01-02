"""
Deals with app config itself.
"""



from enum import Enum
import shutil
import os
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
     SettingsConfigDict,
    TomlConfigSettingsSource,
)

# from platformdirs import user_config_path
# CONFIG_FOLDER = user_config_path("Magician", "vieiraleao2005")

ROOT_FOLDER = Path(__file__).parent.parent.parent.resolve()
CONFIG_FILE_PATH = ROOT_FOLDER / "./config.toml"
SAMPLE_CONFIG_FILE_PATH = ROOT_FOLDER / "./config.sample.toml"

a

class ShellType(Enum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"

class AppConfig(BaseSettings):
    default_shell: ShellType = Field(
        default=ShellType.BASH,
        description="Default shell backend for command syntax",
    )
    examples_folder: Path = Field(
        default=ROOT_FOLDER / "examples/",
        description="Folder for schema storage.",
    )
    schemas_folder: Path = Field(
        default=ROOT_FOLDER / "schemas/",
        description="Folder for schema storage.",
    )
    data_folder: Path = Field(
        default=ROOT_FOLDER / "data/",
        description="Folder for application data and scripts.",
    )

    model_config = SettingsConfigDict(toml_file=CONFIG_FILE_PATH)

    def __init__(self, **_):
        super().__init__(**_)

        os.makedirs(self.data_folder, exist_ok=True)

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: type[BaseSettings], *_, **__
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


def get_config() -> AppConfig:
    if not CONFIG_FILE_PATH.exists():
        raise Exception()
        shutil.copy(SAMPLE_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
        assert CONFIG_FILE_PATH.exists()

    return AppConfig()
