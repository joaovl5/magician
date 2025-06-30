from typing import Callable, Generic, ParamSpec, TypeVar

from .base import BaseCommand

P = ParamSpec("P")
U = TypeVar("U")


class WrapperCommand(Generic[P, U], BaseCommand):
    """Wraps some callable within a command."""

    BACKEND_AGNOSTIC: bool = True

    def __init__(
        self,
        callable: Callable[P, U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__()

        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def run(self, **_) -> U:
        return self.callable(*self.args, **self.kwargs)
