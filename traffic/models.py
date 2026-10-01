from dataclasses import dataclass, field
from typing import Any


@dataclass
class MessageEvent:
    frame_number: int
    timestamp: float
    protocol: str
    kind: str

    src: str | None = None
    dst: str | None = None

    message_type: str | None = None

    related_frames: list[int] = field(default_factory=list)

    correlation: dict[str, Any] = field(default_factory=dict)

    fields: dict[str, Any] = field(default_factory=dict)