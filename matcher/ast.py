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



def build_sequence_ast(sequence_items: list[dict]) -> Sequence:
    """
    Converte la rappresentazione JSON prodotta dal parser DSL nell'AST utilizzato da matcher
    """

    atoms = []

    for item in sequence_items:
       atom = Atom(
           message_type=item["message_type"],
           alias=item["alias"]
       )

       atoms.append(atom)

    return Sequence(items=atoms)