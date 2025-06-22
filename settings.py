"""
Deals with app config itself.
"""

import shutil
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

CONFIG_FILE_PATH = Path("./config.toml")
SAMPLE_CONFIG_FILE_PATH = Path("./config.sample.toml")


class AppConfig(BaseSettings):
    data_folder: Path = Field(
        default=Path("./data/"),
        description="Folder for application data and scripts.",
    )

    model_config = SettingsConfigDict(toml_file=CONFIG_FILE_PATH)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        os.makedirs(self.data_folder, exist_ok=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            file_secret_settings,
        )


def get_config() -> AppConfig:
    if not CONFIG_FILE_PATH.exists():
        shutil.copy(SAMPLE_CONFIG_FILE_PATH, CONFIG_FILE_PATH)
        assert CONFIG_FILE_PATH.exists()

    return AppConfig()
