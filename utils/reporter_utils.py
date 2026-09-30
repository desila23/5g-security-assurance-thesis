from dsl.parse_rule import parse_rule

from utils.evidence_utils import get_events_by_type
from utils.json_utils import load_json, save_json
from utils.verifier_utils import load_test_config, parse_arguments



def operand_to_text(operand):
    value = operand["value"]

    if isinstance(value, bool):
        return str(value).lower()

    return str(value)


def rule_to_expression(rule):
    operator = rule["operator"]

    if operator == "UNIQUE":
        return f"REQUIRE UNIQUE {rule['field']}"

    if operator == "IF":
        return (
            f"IF {rule['field']} "
            f"{rule['condition_operator']} "
            f"{operand_to_text(rule['expected'])}"
        )

    return (
        f"REQUIRE {rule['field']} "
        f"{operator} "
        f"{operand_to_text(rule['expected'])}"        
    )



def load_report_context(
        base_dir,
        test_id,
        case_id=None,
        event_type=None,
        require_single_event=True
):
    test_config = load_test_config(base_dir, test_id, case_id)

    evidence_file = base_dir / test_config["evidence"]
    rule_file = base_dir / test_config["rules"]
    verification_file = base_dir / test_config["output"]

    evidence = load_json(evidence_file)
    verification = load_json(verification_file)

    parsed_rules = parse_rule(rule_file)

    event = None
    if event_type is not None:
        event = get_events_by_type(evidence, event_type, require_single=require_single_event)

    return {
        "config": test_config,
        "evidence": evidence,
        "verification": verification,
        "rules": parsed_rules,
        "event": event        
    }



def run_reporter(
        base_dir,
        description,
        build_report,
        event_type=None,
        require_single_event=True
):
    args = parse_arguments(description)

    context = load_report_context(
        base_dir,
        args.test,
        args.case,
        event_type,
        require_single_event=require_single_event
    )

    report = build_report(args.test, args.case, context)

    output_file = base_dir / context["config"]["report"]

    save_json(output_file, report)

    return report, output_file