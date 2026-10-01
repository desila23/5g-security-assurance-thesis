from dataclasses import dataclass, field

from traffic.models import MessageEvent

@dataclass
class Match:
    start_index: int
    end_index: int

    bindings: dict[str, MessageEvent] = field(default_factory=dict)