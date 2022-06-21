from __future__ import annotations

from dataclasses import dataclass

from discord.ext import commands


@dataclass
class Argument:
    name: str
    annotation: type[commands.Converter] | None
    default: str | None

    def is_optional(self) -> bool:
        return self.default is not None

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'annotation': self.annotation.__name__ if self.annotation else self.annotation,
            'default': self.default
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Argument:
        name = data['name']
        annotation = getattr(commands, data['annotation']) if data['annotation'] else None
        default = data['default']
        return cls(name, annotation, default)
