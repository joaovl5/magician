from pathlib import Path
import sys

from loguru import logger
from magician.config.interpreter import ConfigInterpreter
from magician.config.parser import parse_config_file
from magician.settings import get_config


def main():
    app_cfg = get_config()
    intr = ConfigInterpreter(app_cfg=app_cfg)
    magic_cfg = parse_config_file(file=Path("./draft.yml"))

    logger.remove()
    logger.add(sys.stderr, level="TRACE")

    name = "test"
    intr.compile(config=magic_cfg, schema_name=name)
    # intr.run(config=magic_cfg, schema_name=name)


if __name__ == "__main__":
    main()
