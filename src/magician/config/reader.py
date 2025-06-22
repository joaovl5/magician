from pathlib import Path
from typing import Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from magician.config.schema import MagicConfigSchema


def read_config_file(file: Path) -> Type[MagicConfigSchema]:
    class MagicConfig(MagicConfigSchema):
        model_config = SettingsConfigDict(yaml_file=file)

        @classmethod
        def settings_customise_sources(
            cls, settings_cls: Type[BaseSettings], *args, **kwargs
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (YamlConfigSettingsSource(settings_cls),)

    return MagicConfig()  # type: ignore
