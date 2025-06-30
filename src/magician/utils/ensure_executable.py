import os
import stat
from pathlib import Path

from loguru import logger


def ensure_executable(path: Path):
    """Ensure a script is executable, making it so if needed"""

    if not path.exists():
        raise FileNotFoundError(f"Script not found: {path}")

    if not os.access(path, os.X_OK):
        # Add execute permission for owner, group, and others
        current_mode = path.stat().st_mode
        path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        logger.trace(f"Made {path} executable")
    else:
        logger.trace(f"{path} is already executable")
