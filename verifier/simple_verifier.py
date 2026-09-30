from pathlib import Path

from dsl.parse_rule import parse_rule
from utils.verifier_utils import parse_arguments, load_test_config
from utils.evidence_utils import get_events_by_type
from utils.json_utils import load_json, save_json


BASE_DIR = Path(__file__).resolve().parent.parent


# Funzione per ottenere il valore annidato dal dizionario
def get_nested_value(data, field_path):
    parts = field_path.split(".")

    current = data

    for part in parts:
        if not isinstance(current, dict):
            raise RuntimeError(
                f"Cannot access '{part}': "
                f"the current value is not a JSON object"
            )

        if part not in current:
            raise RuntimeError(
                f"DSL field not found in evidence: '{field_path}' "
                f"(missing '{part}')"
            )

        current = current[part]

    return current


def get_evidence_value(evidence, field_path):
    parts = field_path.split(".")

    event_type = parts[0]
    nested_path = ".".join(parts[1:])

    event = get_events_by_type(
        evidence,
        event_type,
        require_single=True
    )

    return get_nested_value(
        event,
        nested_path
    )




# Confronto semplice
def evaluate_rule(actual_value, operator, expected_value):
    if operator == "==":
        return actual_value == expected_value

    if operator == "!=":
        return actual_value != expected_value

    raise ValueError(
        f"Unsupported operator: {operator}"
    )


# UNIQUE    
def make_hashable(value):
    if isinstance(value, dict):
        return tuple(
            sorted((key, make_hashable(item))
                for key, item in value.items()
            )
        )

    if isinstance(value, list):
        return tuple(make_hashable(item)
            for item in value
        )

    return value


def evaluate_unique_rule(
    evidence,
    field_path
):
    parts = field_path.split(".")

    event_type = parts[0]
    nested_path = ".".join(parts[1:])

    events = get_events_by_type(
        evidence,
        event_type
    )

    occurrences = {}
    observed = []

    for event in events:
        frame = event.get("frame")

        value = get_nested_value(
            event,
            nested_path
        )

        values = (
            value
            if isinstance(value, list)
            else [value]
        )

        observed.append({
            "frame": frame,
            "values": values
        })

        for item in values:
            key = make_hashable(item)

            if key not in occurrences:
                occurrences[key] = {
                    "value": item,
                    "frames": []
                }

            occurrences[key]["frames"].append(
                frame
            )

    duplicates = []

    for occurrence in occurrences.values():
        unique_frames = list(
            dict.fromkeys(
                occurrence["frames"]
            )
        )

        if len(unique_frames) > 1:
            duplicates.append({
                "value": occurrence["value"],
                "frames": unique_frames
            })

    verdict = len(duplicates) == 0

    return verdict, observed, duplicates



def resolve_operand(evidence, operand):
    if operand["type"] == "literal":
        return operand["value"]

    if operand["type"] == "field":
        return get_evidence_value(evidence, operand["value"])

    raise RuntimeError(
        f"Unsupported operand type: {operand['type']}"
    )


def verify_rule(evidence, rule, label):
    operator = rule["operator"]

    # IF
    if operator == "IF":
        return verify_if_rule(evidence, rule, label)



    # UNIQUE
    if operator == "UNIQUE":
        return verify_unique_rule(evidence, rule, label)


    # == / !=
    return verify_comparison_rule(evidence, rule, label)



def verify_if_rule(evidence, rule, label):
    actual_value = get_evidence_value(evidence, rule["field"])
    
    expected = resolve_operand(evidence, rule["expected"])
    
    condition_operator = rule["condition_operator"]
    
    condition_met = evaluate_rule(
        actual_value,
        condition_operator,
        expected
        )
    
    
    print(f"\n--- RULE {label} ---")
    print(f"Condition field: {rule['field']}")
    print(f"Observed: {actual_value}")
    print(f"Condition: {condition_operator}")
    print(f"Expected: {expected}")
    
    if not condition_met:
        print("Verdict: SKIPPED")
    
        return True, {
            "field": rule["field"],
            "operator": "IF",
            "condition_operator": condition_operator,
            "expected": expected,
            "observed": actual_value,
            "verdict": "SKIPPED",
            "rules": []
        }
    
     
    print("Condition matched: evaluating nested rules")

    nested_results = []
    nested_verdict = True
    for index, nested_rule in enumerate(rule["rules"], start=1):
        verdict, result = verify_rule(
            evidence,
            nested_rule,
            f"{label},{index}"
        )
    
        nested_results.append(result)
    
        if not verdict:
            nested_verdict = False
    
    
    return nested_verdict, {
        "field": rule["field"],
        "operator": "IF",
        "condition_operator": condition_operator,
        "expected": expected,
        "observed": actual_value,
        "verdict": "PASS" if nested_verdict else "FAIL",
        "rules": nested_results
    }



def verify_unique_rule(evidence, rule, label):
    verdict, observed, duplicates = evaluate_unique_rule(evidence, rule["field"])

    print(f"\n--- RULE {label} ---")
    print(f"Field: {rule['field']}")
    print("Operator: UNIQUE")

    if duplicates:
        print("Duplicates:")

        for duplicate in duplicates:
            print(
                f"- {duplicate['value']} "
                f"in frames {duplicate['frames']}"
            )
    else:
        print("Duplicates: none")

    print(
        f"Verdict: {'PASS' if verdict else 'FAIL'}"
    )

    return verdict, {
        "field": rule["field"],
        "operator": "UNIQUE",
        "expected": None,
        "observed": observed,
        "duplicates": duplicates,
        "verdict": "PASS" if verdict else "FAIL"
    }



def verify_comparison_rule(evidence, rule, label):
    operator = rule["operator"]

    actual_value = get_evidence_value(evidence, rule["field"])
    expected = resolve_operand(evidence, rule["expected"])
    verdict = evaluate_rule(actual_value, operator, expected)


    print(f"\n--- RULE {label} ---")
    print(f"Field: {rule['field']}")
    print(f"Observed: {actual_value}")
    print(f"Operator: {operator}")
    print(f"Expected: {expected}")
    print(
        f"Verdict: {'PASS' if verdict else 'FAIL'}"
    )
    
    return verdict, {
        "field": rule["field"],
        "operator": operator,
        "expected": expected,
        "observed": actual_value,
        "verdict": "PASS" if verdict else "FAIL"
    }


# =========================
# Verifica della regola
# =========================


def main():
    args = parse_arguments("Verify DSL criteria against a JSON evidence file")

    test_config = load_test_config(
        BASE_DIR,
        args.test,
        args.case
    )

    evidence_file = BASE_DIR / test_config["evidence"]
    rule_file = BASE_DIR / test_config["rules"] 
    output_file = BASE_DIR / test_config["output"]

    evidence = load_json(evidence_file)

    rules = parse_rule(rule_file)


    verification_results = []

    overall_verdict = True


    for index, rule in enumerate(rules, start=1):
        verdict, result = verify_rule(
            evidence,
            rule,
            str(index)
        )

        verification_results.append(result)

        if not verdict:
            overall_verdict = False


    print("\n--- OVERALL VERDICT ---")
    print("PASS" if overall_verdict else "FAIL")


    verification_output = {
        "rules": verification_results,
        "overall_verdict": "PASS" if overall_verdict else "FAIL" 
    }


    save_json(
        output_file,
        verification_output
    )

    print(
        f"\nVerification saved to: {output_file}"
    )



if __name__ == "__main__":
    main()