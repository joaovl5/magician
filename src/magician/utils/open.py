import subprocess
import platform
from typing import List


def open_app(run_cmd: List[str]):
    system = platform.system()

    match system:
        case "Windows":
            subprocess.run(["start", *run_cmd], shell=True)
        case "Darwin":
            subprocess.run(["open", "-a", *run_cmd])
        case "Linux":
            subprocess.run(run_cmd)
        case _:
            raise NotImplementedError(f"Platform name '{system}' not supported!")
