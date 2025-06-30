from typing import Dict, Type

from magician.macros.base import BaseMacro
from magician.macros.python.activate_venv import PythonActivateVenvMacro
from magician.macros.shell.goto_dir import GotoDirectoryMacro


MACRO_MAPPINGS: Dict[str, Type[BaseMacro]] = {
    # user-centred macros
    "python-activate-venv": PythonActivateVenvMacro,
    # special macros (mainly internal usage)
    "goto-dir": GotoDirectoryMacro,
}
