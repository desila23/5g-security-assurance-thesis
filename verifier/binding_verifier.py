from typing import Any

from matcher.models import Match


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


def get_binding_value(match: Match, field_path: str) -> Any:
    """
    Risolve un field path DSL usando i bindings del match.

    Esempio:
        response.status

    diventa:
        match.bindings["response"].fields["status"]
    """

    parts = field_path.split(".")

    if len(parts) < 2:
        raise RuntimeError(
            f"Invalid binding field path: '{field_path}'"
        )

    alias = parts[0]
    nested_path = ".".join(parts[1:])

    if alias not in match.bindings:
        raise RuntimeError(
            f"Binding '{alias}' not found"
        )

    event = match.bindings[alias]

    return get_nested_value(event.fields, nested_path)


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


def resolve_operand(match: Match, operand: dict) -> Any:
    if operand["type"] == "literal":
        return operand["value"]

    if operand["type"] == "field":
        return get_binding_value(match, operand["value"])

    raise RuntimeError(
        f"Unsupported operand type: {operand['type']}"
    )


def verify_comparison_rule(match: Match, rule: dict) -> tuple[bool, dict]:
    operator = rule["operator"]

    actual_value = get_binding_value(match, rule["field"])

    expected_value = resolve_operand(match, rule["expected"])

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


def verify_match(match: Match, rules: list[dict]) -> dict:
    results = []
    overall_verdict = True

    for rule in rules:
        operator = rule["operator"]

        if operator not in {"==", "!="}:
            raise ValueError(
                f"Unsupported operator in binding verifier: '{operator}'"
            )

        verdict, result = verify_comparison_rule(match, rule)

        results.append(result)

        if not verdict:
            overall_verdict = False

    return {
        "rules": results,
        "overall_verdict": (
            "PASS" if overall_verdict
            else "FAIL"
        ),
    }