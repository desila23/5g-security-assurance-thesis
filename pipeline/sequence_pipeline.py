from dataclasses import dataclass, field

from dsl.parse_rule import get_sequence, parse_rule

from matcher.ast import build_sequence_ast
from matcher.models import BindingContext, Match
from matcher.thompson import ThompsonCompiler
from matcher.matcher import match_sequence

from traffic.models import MessageEvent

from verifier.binding_verifier import verify_bindings


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
    external_bindings: dict | None = None
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
        match = match_sequence(nfa, group)

        if match is not None:
            matches.append(match)

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