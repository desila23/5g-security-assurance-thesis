from matcher.automaton import NFA, Transition
from matcher.models import Match
from traffic.models import MessageEvent

def _get_transition(nfa: NFA, state: int) -> Transition | None:
    """
    Restituisce la transizione non-epsilon uscente dallo stato
    Per ora assumiamo un automa lineare, in cui ogni stato ha al massimo una transizione consumante.
    """

    transitions = [
        transition for transition in nfa.transitions
        if (
            transition.source == state 
            and transition.atom is not None
        )
    ]

    if not transitions:
        return None

    if len(transitions) > 1:
        raise ValueError(
            f"Linear matcher found multiple ouutgoing transition from state {state}"
        )

    return transitions[0]


def match_sequence(nfa: NFA, events: list[MessageEvent]) -> Match | None:
    """
    Cerca il primo match completo dell'NFA nella lista di eventi.
    Gli eventi che non corrispondono alla transizione corrente vengono ignorati.
    """

    current_state = nfa.start_state

    bindings = {}

    start_index = None
    end_index = None

    for index, event in enumerate(events):
        transition = _get_transition(nfa, current_state)

        if transition is None:
            break

        expected = transition.atom.message_type

        if event.message_type != expected:
            continue

        if start_index is None:
            start_index = index

        bindings[transition.atom.alias] = event

        current_state = transition.target
        end_index = index

        if current_state == nfa.accept_state:
            return Match(
                start_index=start_index,
                end_index=end_index,
                bindings=bindings
            )

    return None