from typing import Any

from matcher.models import BindingContext, Match
from traffic.models import MessageEvent



class MissingEvidenceError(Exception):
    def __init__(self, field_path: str, alias: str):
        self.field_path = field_path
        self.alias = alias
        super().__init__(
            f"Required binding '{alias}' not available"
        )



def get_nested_value(data: dict, field_path: str) -> Any:
    """
    Recupera un valore annidato da un dizionario.

    Esempio:
        data = {
            "body": {
                "nfType": "SMF"
            }
        }

        field_path = "body.nfType"

        risultato = "SMF"
    """

    parts = field_path.split(".")

    current = data

    for part in parts:
        if not isinstance(current, dict):
            raise RuntimeError(
                f"Cannot access '{part}': the current value is not a dictionary"
            )

        if part not in current:
            raise RuntimeError(
                f"Field not found: '{field_path}' (missing '{part}')"
            )

        current = current[part]

    return current


def get_event_field(event: MessageEvent, field_path: str) -> Any:
    return get_nested_value(event.fields, field_path)


def get_binding_value(context: BindingContext, field_path: str) -> Any:
    """
    Risolve un field path DSL utilizzando un BindingContext.

    Binding singolo:
        response.status
    Con:
        response -> MessageEvent
    restituisce:
        response.fields["status"]

    Binding multiplo:
        responses.f_tied
    Con:
        responses -> list[MessageEvent]
    Restituisce una lista che mantiene frame e valore per ogni evento della collezione.    
    """

    parts = field_path.split(".")

    if len(parts) < 2:
        raise RuntimeError(
            f"Invalid binding field path: '{field_path}'"
        )

    alias = parts[0]
    nested_path = ".".join(parts[1:])

    if alias not in context.bindings:
        raise MissingEvidenceError(
            field_path=field_path,
            alias=alias,
        )

    binding = context.bindings[alias]

    # Binding multiplo
    if isinstance(binding, list):
        return [
            {
                "frame": event.frame_number,
                "value": get_event_field(event, nested_path)
            }
            for event in binding
        ]

    # Binding esterno / configurativo
    if isinstance(binding, dict):
        return get_nested_value(binding, nested_path)

    # Binding singolo
    return get_event_field(binding, nested_path)
    


def evaluate_rule(
    actual_value: Any,
    operator: str,
    expected_value: Any,
) -> bool:
    if operator == "==":
        return actual_value == expected_value

    if operator == "!=":
        return actual_value != expected_value

    raise ValueError(
        f"Unsupported operator: {operator}"
    )


def resolve_operand(context: BindingContext, operand: dict) -> Any:
    if operand["type"] == "literal":
        return operand["value"]

    if operand["type"] == "field":
        return get_binding_value(context, operand["value"])

    raise RuntimeError(
        f"Unsupported operand type: {operand['type']}"
    )


def make_hashable(value: Any):
    if isinstance(value, dict):
        return tuple(
            sorted(
                (key, make_hashable(item))
                for key, item in value.items()
            )
        )

    if isinstance(value, list):
        return tuple(
            make_hashable(item)
            for item in value
        )

    return value



def verify_comparison_rule(context: BindingContext, rule: dict) -> tuple[bool, dict]:
    operator = rule["operator"]

    actual_value = get_binding_value(context, rule["field"])

    expected_value = resolve_operand(context, rule["expected"])

    verdict = evaluate_rule(
        actual_value,
        operator,
        expected_value,
    )

    result = {
        "field": rule["field"],
        "operator": operator,
        "expected": expected_value,
        "observed": actual_value,
        "verdict": "PASS" if verdict else "FAIL",
    }

    if rule["expected"]["type"] == "field":
        result["expected_field"] = rule["expected"]["value"]

    return verdict, result


def verify_unique_rule(context: BindingContext, rule:dict) -> tuple[bool, dict]:
    observed = get_binding_value(
        context,
        rule["field"]
    )

    occurrences = {}

    for entry in observed:
        frame = entry["frame"]
        value = entry["value"]

        values = (
            value if isinstance(value, list) 
            else [value]
        )

        for item in values:
            key = make_hashable(item)

            if key not in occurrences:
                occurrences[key] = {
                    "value": item,
                    "frames": []
                }

            occurrences[key]["frames"].append(frame)

    duplicates = []

    for occurrence in occurrences.values():
        unique_frames = list(
            dict.fromkeys(occurrence["frames"])
        )

        if len(unique_frames) > 1:
            duplicates.append({
                "value": occurrence["value"],
                "frames": unique_frames
            })

    verdict = len(duplicates) == 0

    return verdict, {
        "field": rule["field"],
        "operator": "UNIQUE",
        "expected": None,
        "observed": observed,
        "duplicates": duplicates,
        "verdict": (
            "PASS" if verdict
            else "FAIL" 
        )           
    }



def aggregate_verdicts(verdicts: list[str]) -> str:
    """
    Aggregazione congiuntiva dei criteri applicabili.

    FAIL > INCONCLUSIVE > PASS.
    SKIPPED è neutro.
    """

    if "FAIL" in verdicts:
        return "FAIL"

    if "INCONCLUSIVE" in verdicts:
        return "INCONCLUSIVE"

    return "PASS"


def verify_if_rule(context: BindingContext, rule: dict) -> tuple[bool, dict]:
    actual_value = get_binding_value(context, rule["field"])
    expected_value = resolve_operand(context, rule["expected"])

    condition_operator = rule["condition_operator"]

    condition_met = evaluate_rule(
        actual_value,
        condition_operator,
        expected_value
    )


    # Se la condizione NON riguarda il caso attuale, viene "skippata"
    if not condition_met:
        return "SKIPPED", {
            "field": rule["field"],
            "operator": "IF",
            "condition_operator": condition_operator,
            "expected": expected_value,
            "observed": actual_value,
            "verdict": "SKIPPED",
            "rules": []            
        }


    nested_results = []
    nested_verdictS = []

    for nested_rule in rule["rules"]:
        verdict, result = verify_rule(context, nested_rule)

        nested_results.append(result)
        nested_verdictS.append(verdict)

    overall = aggregate_verdicts(nested_verdictS)

    return overall, {
        "field": rule["field"],
        "operator": "IF",
        "condition_operator": condition_operator,
        "expected": expected_value,
        "observed": actual_value,
        "verdict": overall,
        "rules": nested_results
    }



def verify_rule(context: BindingContext, rule: dict) -> tuple[bool, dict]:
    operator = rule["operator"]

    try:
        if operator == "IF":
            return verify_if_rule(context, rule)

        if operator in {"==", "!="}:
            passed, result = verify_comparison_rule(context, rule)
            return ("PASS" if passed else "FAIL"), result

        if operator == "UNIQUE":
            passed, result = verify_unique_rule(context, rule)
            return ("PASS" if passed else "FAIL"), result

        raise ValueError(
            f"Unsupported operator in binding verifier: '{operator}'"
        )

    except MissingEvidenceError as exc:
        expected_operand = rule.get("expected", {})

        expected = None
        expected_field = None

        if isinstance(expected_operand, dict):
            if expected_operand.get("type") == "literal":
                expected = expected_operand.get("value")
            elif expected_operand.get("type") == "field":
                expected_field = expected_operand.get("value")

        result = {
            "field": rule["field"],
            "operator": operator,
            "expected": expected,
            "observed": None,
            "verdict": "INCONCLUSIVE",
            "reason": "required_binding_missing",
            "missing_binding": exc.alias,
            "missing_field_path": exc.field_path,
        }

        if expected_field is not None:
            result["expected_field"] = expected_field

        if operator == "IF":
            result["condition_operator"] = rule["condition_operator"]
            result["rules"] = []

        return "INCONCLUSIVE", result
    


def verify_bindings(context: BindingContext, rules: list[dict]) -> dict:
    """
    Verifica le regole DSL utilizzando una semantica a tre verdetti: PASS, FAIL, INCONCLUSIVE.

    I criteri non applicabili (SKIPPED) sono neutri.
    """

    results = []
    verdicts = []

    for rule in rules:
        verdict, result = verify_rule(context, rule)

        results.append(result)
        verdicts.append(verdict)

    return {
        "rules": results,
        "overall_verdict": aggregate_verdicts(verdicts)
    }


def verify_match(match: Match, rules: list[dict]) -> dict:
    """
    Wrapper di compatibilità per i sequence test già esistenti.

    NRF e AMF possono continuare a chiamare verify_match().
    """

    context = match.to_binding_context()

    return verify_bindings(
        context,
        rules
    )