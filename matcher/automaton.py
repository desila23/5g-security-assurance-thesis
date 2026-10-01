from dataclasses import dataclass, field

from matcher.ast import Atom

@dataclass
class Transition:
    source: int
    target: int
    atom: Atom | None = None


@dataclass
class NFA:
    """
    Rappresenta un automa a stati finiti non deterministico
    """
    start_state: int
    accept_state: int
    transitions: list[Transition] = field(default_factory=list)