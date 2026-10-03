from dataclasses import dataclass, field

from matcher.automaton import NFA, Transition
from matcher.models import Match
from traffic.models import MessageEvent


@dataclass
class ActiveConfiguration:
    state: int
    bindings: dict[str, MessageEvent] = field(default_factory=dict)


def _configuration_key(configuration: ActiveConfiguration):
    return (
        configuration.state,
        tuple(
            sorted(
                (alias, event.frame_number)
                for alias, event in configuration.bindings.items()
            )
        )
    )


def _deduplicate_configurations(configurations: list[ActiveConfiguration]) -> list[ActiveConfiguration]:

    unique = {}

    for configuration in configurations:
        key = _configuration_key(configuration)

        if key not in unique:
            unique[key] = configuration

    return list(unique.values())



def _get_transitions(nfa: NFA, state: int) -> list[Transition]:
    """
    Restituisce tutte le transizioni uscenti da uno stato, incluse le epsilon transition.
    """

    return [
        transition for transition in nfa.transitions
        if transition.source == state
    ]


def _get_epsilon_transitions(nfa: NFA, state: int) -> list[Transition]:
    return [
        transition for transition in _get_transitions(nfa, state)
        if transition.atom is None
    ]


def _get_consuming_transitions(nfa: NFA, state: int) -> list[Transition]:
    return [
        transition for transition in _get_transitions(nfa, state)
        if transition.atom is not None
    ]


def epsilon_closure(nfa: NFA, states: set[int]) -> set[int]:
    """
    Restituisce tutti gli stati raggiungibili dagli stati iniziali utilizzando zero o più epsilon transizioni
    """

    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()

        for transition in _get_epsilon_transitions(nfa, state):
            target = transition.target

            if target not in closure:
                closure.add(target)
                stack.append(target)

    return closure


def expand_configuration(nfa: NFA, configuration: ActiveConfiguration) -> list[ActiveConfiguration]:
    states = epsilon_closure(nfa, {configuration.state})

    return [
        ActiveConfiguration(
            state=state,
            bindings=dict(configuration.bindings)
        )
        for state in states
    ]



def advance_configurations(
        nfa: NFA,
        configurations: list[ActiveConfiguration],
        event: MessageEvent
) -> list[ActiveConfiguration]:

    next_configurations = []

    for configuration in configurations:
        expanded = expand_configuration(nfa, configuration)

        for current in expanded:
            transitions = _get_consuming_transitions(nfa, current.state)

            for trantision in transitions:
                if event.message_type != trantision.atom.message_type:
                    continue

                bindings = dict(current.bindings)

                bindings[trantision.atom.alias] = event

                next_configuration = (
                    ActiveConfiguration(
                        state=trantision.target,
                        bindings=bindings
                    )
                )

                next_configurations.extend(
                    expand_configuration(nfa, next_configuration)
                )

    return _deduplicate_configurations(next_configurations)


def process_event(
        nfa: NFA,
        configurations: list[ActiveConfiguration],
        event: MessageEvent
) -> list[ActiveConfiguration]:
    """
    Processa un evento della trace.

    Per ogni configuraizone:
        - se l'evento può essere consumato, avanza;
        - altrimenti mantiene la configurazione invariata, trattando l'evento come irrilevante.
    """

    next_configurations = []

    configurations = _deduplicate_configurations(configurations)

    for configuration in configurations:
        expanded = expand_configuration(nfa, configuration)

        expanded = _deduplicate_configurations(expanded)

        for current in expanded:
            matching_transitions = [
                transition for transition in _get_consuming_transitions(nfa, current.state)
                if transition.atom.message_type == event.message_type
            ]

        # Caso 1: evento rilevante per la configurazione
        if matching_transitions:
            for transition in matching_transitions:
                bindings = dict(current.bindings)

                bindings[transition.atom.alias] = event

                advanced = ActiveConfiguration(
                    state=transition.target,
                    bindings=bindings
                )

                next_configurations.extend(
                    expand_configuration(nfa, advanced)
                )

        # Caso 2: evento irrilevante per la configurazione
        else:
            next_configurations.append(current)

    return _deduplicate_configurations(next_configurations)



def can_start_with_event(nfa: NFA, event: MessageEvent) -> bool:
    start_states = epsilon_closure(nfa, {nfa.start_state})

    for state in start_states:
        for transition in _get_consuming_transitions(nfa, state):
            if transition.atom.message_type == event.message_type:
                return True

    return False



def configurations_can_consume(
        nfa: NFA,
        configurations: list[ActiveConfiguration],
        event: MessageEvent
) -> bool:
    """
    Restituisce TRUE se almeno una configurazione attiva può consumare l'evento, 
    considerando anche le epsilon transizioni raggiungibili dallo stato corrente.
    """

    for configuration in configurations:
        expanded = expand_configuration(nfa, configuration)

        expanded = _deduplicate_configurations(expanded)

        for current in expanded:
            for transition in _get_consuming_transitions(nfa, current.state):
                if transition.atom.message_type == event.message_type:
                    return True

    return False
    


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

    for start_index, start_event in enumerate(events):
        # Non ha senso creare un candidato se questo evento NON può iniziare il pattern.
        if not can_start_with_event(nfa, start_event):
            continue

        configurations = [
            ActiveConfiguration(state=nfa.start_state)
        ]

        configurations = expand_configuration(nfa, configurations[0])

        configurations = _deduplicate_configurations(configurations)

        for index in range(start_index, len(events)):
            event = events[index]

            # RESTART POLICY:
            # Se compare un nuovo possibile inizio del pattern, ma il candidato corrente non può consumarlo
            # allora il candidato appartiene a un tentativo precedente e non viene invalidato.
            if(
                index > start_index
                and can_start_with_event(nfa, event)
                and not configurations_can_consume(nfa, configurations, event)
            ):
                break

            configurations = process_event(nfa, configurations, event)

            accepting = [
                configuration for configuration in configurations
                if configuration.state == nfa.accept_state
            ]

            if not accepting:
                continue

            for configuration in accepting:
                matches.append(
                    Match(
                        start_index=start_index,
                        end_index=index,
                        bindings=dict(configuration.bindings)
                    )
                )

            # Per questo candidato ci interessa il primo completamento.
            break

    return _filter_dominated_matches(matches)



def _match_dominates(candidate: Match, other: Match) -> bool:
    """
    Restituisce True se candidate rappresenta una versione strettamente più completa di other sullo stesso intervallo.

    La dominanza richiede:
        - stesso start_index;
        - stesso end_index;
        - tutti i binding di other presenti anche in candidate;
        - stessi eventi per i binding condivisi;
        - almeno un binding aggiuntivo in candidate.
    """

    if (
        candidate.start_index != other.start_index
        or candidate.end_index != other.end_index
    ):
        return False

    candidate_aliases = set(candidate.bindings.keys())
    other_aliases = set(other.bindings.keys())

    # Other deve essere un sottoinsieme stretto.
    if not other_aliases < candidate_aliases:
        return False

    # I binding condivisi devono riferirsi agli stessi eventi della trace.
    for alias in other_aliases:
        candidate_event = candidate.bindings[alias]
        other_event = other.bindings[alias]

        if candidate_event.frame_number != other_event.frame_number:
            return False

    return True


def _filter_dominated_matches(matches: list[Match]) -> list[Match]:
    """
    Elimina i match dominanti da un altro match sullo stesso intervallo temporale.
    """

    filtered = []

    for match in matches:
        dominated = any(
            _match_dominates(other, match) 
            for other in matches
            if other is not match
        )

        if not dominated:
            filtered.append(match)

    return filtered