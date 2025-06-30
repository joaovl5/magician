from abc import ABC, abstractmethod
from typing import Any, Tuple

from magician.config.schema import WizardBackendType


class BaseCommand(ABC):
    BACKEND_AGNOSTIC: bool = False
    SUPPORTED_BACKENDS: Tuple[WizardBackendType, ...] = ()

    def __init__(self, **_) -> None:
        if not self.BACKEND_AGNOSTIC:
            if len(self.SUPPORTED_BACKENDS) == 0:
                raise NotImplementedError(
                    "Command must have at least one supported backend."
                )

    @abstractmethod
    def run(self, **_) -> Any: ...
