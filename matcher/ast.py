from dataclasses import dataclass

class PatternNode:
    """
    Classe base per tutti i nodi dell'AST dei pattern
    """

    pass


@dataclass
class Atom(PatternNode):
    """
    Rappresenta un singolo tipo di messaggio atteso (es. nrf.discovery.request as request)
    """

    message_type: str
    alias: str

@dataclass
class Sequence(PatternNode):
    """
    Rappresenta una sequenza ordinata di pattern (es. request response)
    """

    items: list[PatternNode]

@dataclass
class Optional(PatternNode):
    """
    Rappresenta un pattern opzionale che può essere consumato oppure saltato tramite epsilon transition.
    """

    items: list[PatternNode]


def build_pattern_node(item: dict) -> PatternNode:
    if item.get("operator") == "OPTIONAL":
        return Optional(
            items=[
                build_pattern_node(child)
                for child in item["items"]
            ]
        )

    return Atom(
        message_type=item["message_type"],
        alias=item["alias"]
    )


def build_sequence_ast(sequence_items: list[dict]) -> Sequence:
    return Sequence(
        items=[
            build_pattern_node(item)
            for item in sequence_items
        ]
    )