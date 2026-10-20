from dataclasses import dataclass, field

from dsl.parse_rule import get_collect, parse_rule

from matcher.collector import collect_events
from matcher.models import BindingContext

from traffic.models import MessageEvent

from verifier.binding_verifier import verify_bindings
from verifier.dsl_alias_validator import validate_rule_aliases


@dataclass
class CollectVerificationResult:
    verdict: str

    context: BindingContext | None = None

    verification: dict | None = None

    details: dict = field(default_factory=dict)


def run_collect_verification(events: list[MessageEvent], rule_file: str) -> CollectVerificationResult:
    """
    Esegue una verifica collection-based.

    Pipeline:
        DSL COLLECT
        -> event filtering
        -> BindingContext
        -> static verification
        -> verdict
    """

    collect = get_collect(rule_file)
    rules = parse_rule(rule_file)

    # L'alias dichiarato da COLLECT è disponibile
    # come riferimento valido nei criteri DSL.
    declared_aliases = {collect["alias"]}

    # Controllo strutturale prima della raccolta degli eventi.
    validate_rule_aliases(rules, declared_aliases)

    context = collect_events(
        events,
        message_type=collect["message_type"],
        alias=collect["alias"],
    )

    collected = context.bindings.get(
        collect["alias"],
        []
    )

    if not collected:
        return CollectVerificationResult(
            verdict="INCONCLUSIVE",
            context=context,
            details={
                "reason": (
                    f"No events collected for {collect['message_type']}"
                ),
                "message_type": collect["message_type"],
                "alias": collect["alias"],
                "collected_events": 0
            },
        )

    verification = verify_bindings(context, rules)

    return CollectVerificationResult(
        verdict=verification["overall_verdict"],
        context=context,
        verification=verification,
        details={
            "collected_events": len(collected),
            "alias": collect["alias"],
            "message_type": collect["message_type"],
        },
    )