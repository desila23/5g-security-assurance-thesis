from dataclasses import dataclass, field

from dsl.parse_rule import get_sequence, parse_rule

from matcher.ast import build_sequence_ast
from verifier.dsl_alias_validator import collect_sequence_aliases, validate_rule_aliases
from matcher.models import BindingContext, Match
from matcher.thompson import ThompsonCompiler
from matcher.matcher import match_sequences

from traffic.models import MessageEvent

from verifier.binding_verifier import verify_bindings

from utils.derived_binding_utils import build_derived_bindings



@dataclass
class SequenceVerificationResult:
    verdict: str

    match: Match | None = None
    context: BindingContext | None = None

    verification: dict | None = None

    details: dict = field(default_factory=dict)


def group_events_by_correlation(events: list[MessageEvent]) -> list[list[MessageEvent]]:
    """
    Raggruppa gli eventi utilizzando la loro correlation key.

    Per gli eventi HTTP/2 attuali la chiave è:
        (tcp_stream, http2_stream_id)

    Eventi privi di correlazione vengono temporaneamente
    considerati gruppi indipendenti.
    """

    groups = {}

    uncorrelated = []

    for event in events:
        if event.correlation:
            key = tuple(sorted(event.correlation.items()))

            groups.setdefault(key, []).append(event)

        else:
            uncorrelated.append([event])

    result = list(groups.values())
    result.extend(uncorrelated)

    for group in result:
        group.sort(
            key=lambda event: (
                event.timestamp,
                event.frame_number,
            )
        )

    return result


def run_sequence_verification(
    events: list[MessageEvent],
    rule_file: str,
    correlation_mode: str = "grouped",
    external_bindings: dict | None = None,
    config_bindings: dict | None = None,
    derived_bindings: dict | None = None
) -> SequenceVerificationResult:
    """
    Esegue una verifica sequence-based su eventi semantici.

    Pipeline:
        DSL
        → AST
        → NFA
        → correlation grouping
        → sequence matching
        → static verification
        → verdict
    """

    sequence = get_sequence(rule_file)
    rules = parse_rule(rule_file)

    # Alias dichiarati nella SEQUENCE, inclusi gli OPTIONAL
    declared_aliases = collect_sequence_aliases(sequence)

    # Alias forniti dall'esterno o dalla configurazione
    declared_aliases.update((external_bindings or {}).keys())
    declared_aliases.update((config_bindings or {}).keys())

    # Alias derivati dichiarati nella configurazione
    declared_aliases.update((derived_bindings or {}).keys())

    # Validazione strutturale della DSL
    # Da eseguire prima del matching, anche quando non ci sono match
    validate_rule_aliases(rules, declared_aliases)

    ast = build_sequence_ast(sequence)

    nfa = ThompsonCompiler().compile(ast)


    if correlation_mode == "global":
        groups = [
            sorted(
                events,
                key=lambda event: (
                    event.timestamp,
                    event.frame_number
                )
            )
        ]

    elif correlation_mode == "grouped":
        groups = group_events_by_correlation(events)

    else:
        raise ValueError(
            f"Unsupported correlation mode: {correlation_mode}"
        )


    matches = []

    for group in groups:
        group_matches = match_sequences(nfa, group)

        matches.extend(group_matches)

    if not matches:
        return SequenceVerificationResult(
            verdict="INCONCLUSIVE",
            details={
                "reason": "No complete sequence match found",
                "candidate_groups": len(groups),
            },
        )

    #
    # Per ora i sequence test richiedono un singolo match.
    # La cardinalità verrà resa esplicita nella DSL più avanti.
    #
    if len(matches) > 1:
        return SequenceVerificationResult(
            verdict="INCONCLUSIVE",
            details={
                "reason": "Multiple complete sequence matches found",
                "matches_found": len(matches),
            },
        )

    match = matches[0]

    context = match.to_binding_context()
    

    if external_bindings:
        context.bindings.update(external_bindings)

    if config_bindings:
        context.bindings.update(config_bindings)

    if derived_bindings:
        computed_bindings = build_derived_bindings(context, derived_bindings)

        context.bindings.update(computed_bindings)
        
    verification = verify_bindings(context, rules)

    return SequenceVerificationResult(
        verdict=verification["overall_verdict"],
        match=match,
        context=context,
        verification=verification,
        details={
            "matches_found": 1,
        },
    )