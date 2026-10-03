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
    Restituisce il primo match completo trovato.

    La logica di matching è centralizzata in match_sequences().
    """

    matches = match_sequences(nfa, events)

    return matches[0] if matches else None



def match_sequences(nfa: NFA, events: list[MessageEvent]) -> list[Match]:
    """
    Cerca tutti i match completi dell'NFA nella lista di eventi.

    Ogni evento compatibile con la prima transizione può avviare un nuovo candidato indipendente.
    
    Dopo l'avvio del canditato, gli eventi non compatibili con la transizione corrente vengono ignorati.
    """

    matches = []

    first_transition = _get_transition(nfa, nfa.start_state)

    if first_transition is None:
        return matches
    

    for start_index in range(len(events)):
        start_event = events[start_index]

        # Un canditato può iniziare solo da un evento compatibile con la prima transizione
        if start_event.message_type != first_transition.atom.message_type:
            continue


        current_state = nfa.start_state
        bindings = {}

        for index in range(start_index, len(events)):
            event = events[index]

            transition = _get_transition(nfa, current_state)

            if transition is None:
                break

            expected = transition.atom.message_type

            if event.message_type != expected:
                # Se compare un nuovo possibile inizio della sequenza, il candidato corrente viene invalidato.
                if (
                    index > start_index 
                    and event.message_type == first_transition.atom.message_type
                ):
                    break
                
                continue


            bindings[transition.atom.alias] = event
            current_state = transition.target


            if current_state == nfa.accept_state:
                matches.append(
                    Match(
                        start_index=start_index,
                        end_index=index,
                        bindings=dict(bindings)
                    )
                )

                break

    return matches


