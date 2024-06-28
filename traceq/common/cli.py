from argparse import ArgumentParser, Namespace, Action
from .transformers import unique


__all__ = ["AppendUnique"]


class AppendUnique(Action):
    def __call__(
        self,
        _: ArgumentParser,
        namespace: Namespace,
        value: str,
        __: None = None,
    ) -> None:
        old_value = getattr(namespace, self.dest) or []
        new_value = old_value + [value]

        unique_values = unique(new_value)
        setattr(namespace, self.dest, unique_values)
