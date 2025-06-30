from pathlib import Path
import pytest

from magician.settings import AppConfig


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    return AppConfig.model_validate(
        {
            "data_folder": Path("./test_data/"),
        }
    )
