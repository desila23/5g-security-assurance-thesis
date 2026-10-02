from dataclasses import dataclass, field
from typing import Any, TypeAlias

from traffic.models import MessageEvent


BindingValue: TypeAlias = (
    MessageEvent
    | list[MessageEvent]
    | dict[str, Any]
)


@dataclass
class BindingContext:
    bindings: dict[str, BindingValue] = field (default_factory=dict)


@dataclass
class Match:
    start_index: int
    end_index: int

    bindings: dict[str, MessageEvent] = field(default_factory=dict)

    def to_binding_context(self) -> BindingContext:
        return BindingContext(bindings=dict(self.bindings))