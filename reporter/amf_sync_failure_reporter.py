from pathlib import Path

from utils.json_utils import load_json

import utils.reporter_utils as reporter_utils
from utils.report_schema import normalize_report


BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_TYPE = "amf_sync_failure"


# EVIDENCE FRAMES
def get_frames_for_field(event, field_path):
    parts = field_path.split(".")

    # rimuovo il tipo "evento"
    nested_parts = parts[1:]

    if not nested_parts:
        return []


    section = nested_parts[0]
    section_data = event.get(section)

    if not isinstance(section_data, dict):
        return []


    frame = section_data.get("frame")

    if frame is None:
        return []

    return [frame]    



# TEMPORAL CRITERION
def build_temporal_criterion(
        case,
        criterion_id,
        temporal_policy,
        temporal_verification,
        timer_config,
        event
):
    timing = event["timing"]

    if case == "A":
        start_event = event["resynchronization_request"]
        end_event = event["ausf_authentication_response"]

        description = "After the resynchronization request, the AUSF Authentication Response must be received before T3520 expires"

        observed_interval = timing["resynchronization_request_to_ausf_response_seconds"]

    elif case == "B":
        start_event = event["synchronization_failure"]
        end_event = event["subsequent_authentication_request"]

        description = "After a synchronization failure, the AMF must not send a new Authentication Request while T3520 is running"

        observed_interval = timing["sync_failure_to_next_authentication_request_seconds"]

    else:
        raise RuntimeError(
            f"Unsupported AMF synchronization failure case: {case}"
        )


    criterion = {
        "id": criterion_id,

        "type": "temporal",

        "description": description,

        "specification": {
            "language": "MFOTL",
            "expression": " ".join(temporal_policy.split())
        },

        "timer": {
            "name": timer_config["name"],
            "duration_ms": timer_config["duration_ms"]
        }
    }


    evidence_frames = []

    if start_event is not None and start_event.get("frame") is not None:
        evidence_frames.append(start_event["frame"])

    if end_event is not None and end_event.get("frame") is not None:
        evidence_frames.append(end_event["frame"])


    result = {
        "criterion_id": criterion_id,

        "engine": temporal_verification["engine"],

        "verification_mode": (temporal_verification["verification_mode"]),

        "violation_found": (temporal_verification["violation_found"]),

        "monpoly_output": (temporal_verification["monpoly_output"]),

        "observed_interval_seconds": observed_interval,

        "evidence_frames": evidence_frames,

        "verdict": (temporal_verification["overall_verdict"])
    }


    return criterion, result


# NB: case_id qui non serve
def build_report(test_id, case_id, context):
    test_config = context["config"]

    case = test_config["case"]

    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]
    event = context["event"]


    temporal_config = test_config["temporal"]

    temporal_verification_file = BASE_DIR / temporal_config["output"]
    formula_file = BASE_DIR / temporal_config["generated_formula"]
    timer_config = temporal_config["timer"]

    temporal_verification = load_json(temporal_verification_file)


    with open(formula_file, "r", encoding="utf-8") as f:
        temporal_policy = f.read().strip()


    criteria = []
    verification_results = []


    # CRITERI STATICI DSL
    for index, (parsed_rule, verification_rule) in enumerate(
        zip (parsed_rules, verification["rules"]), start=1
    ):

        criterion_id = f"criterion_{index}"

        evidence_frames = get_frames_for_field(event, parsed_rule["field"])


        expression = reporter_utils.rule_to_expression(parsed_rule)

        criteria.append({
            "id": criterion_id,

            "type": "comparison",

            "description": (
                f"Verification of "
                f"{verification_rule['field']} "
                f"{verification_rule['operator']} "
                f"{verification_rule['expected']}"
            ),

            "specification": {
                "language": "DSL",
                "expression": expression
            }
        })

        verification_results.append({
            "criterion_id": criterion_id,

            "engine": "simple_verifier",

            "field": verification_rule["field"],

            "operator": verification_rule["operator"],

            "expected": verification_rule["expected"],

            "observed": verification_rule["observed"],

            "evidence_frames": evidence_frames,

            "verdict": verification_rule["verdict"]
        })



    # CRITERIO TEMPORALE MFOTL
    temporal_criterion_id = f"criterion_{len(criteria) + 1}"

    temporal_criterion, temporal_result = build_temporal_criterion(
        case,
        temporal_criterion_id,
        temporal_policy,
        temporal_verification,
        timer_config,
        event
    )

    criteria.append(temporal_criterion)

    verification_results.append(temporal_result)


    # VERDETTO COMPLESSIVO
    overall_verdict = (
        "PASS" if all(
            result["verdict"] == "PASS"
            for result in verification_results
        )
        else "FAIL"
    )



    # Spiegazione
    sync_failure = event["synchronization_failure"]

    resync_request = event["resynchronization_request"]
    
    ausf_response = event["ausf_authentication_response"]

    next_auth_request = event["subsequent_authentication_request"]

    timing = event["timing"]

    explanation = {
        "case": case,

        "synchronization_failure_cause": sync_failure["cause"],

        "auts_present": sync_failure["auts_present"],

        "resynchronization_request_present": resync_request["present"],

        "ausf_authentication_response_present": ausf_response["present"],

        "subsequent_authentication_request_present": next_auth_request["present"],

        "sync_failure_to_next_authentication_request_seconds": timing["sync_failure_to_next_authentication_request_seconds"],

        "resynchronization_request_to_ausf_response_seconds": timing["resynchronization_request_to_ausf_response_seconds"],

        "timer": {
            "name": timer_config["name"],

            "duration_seconds": timer_config["duration_ms"] / 1000
        }
    }


    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "source_test_name": f"TC_SYNC_FAIL_SEAF_AMF - Test {case}",

            "nf": "AMF",

            "description": "Verification of synchronization failure handling by the SEAF/AMF, including the temporal constraint associated with T3520"
        },

        "source": evidence["source"],

        "criteria": criteria,

        "verification": {
            "results": verification_results,

            "overall_verdict": overall_verdict
        },

        "evidence": event,

        "explanation": explanation,

        "verdict": overall_verdict
    }


    interval = temporal_result["observed_interval_seconds"]
    threshold = timer_config["duration_ms"] / 1000

    if case == "A":
        summary = (
            f"Case A: the AUSF response followed the resynchronization "
            f"request after {interval:g} s (T3520: {threshold:g} s). "
        )
    else:
        summary = (
            f"Case B: the AMF sent another Authentication Request "
            f"{interval:g} s after the synchronization failure "
            f"(T3520: {threshold:g} s). "
        )

    summary += (
        f"Static verdict: {verification['overall_verdict']}; "
        f"temporal verdict: {temporal_verification['overall_verdict']}."
    )

    return normalize_report(report, summary)



def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR,
        "Generate AMF synchronization failure report",
        build_report,
        EVENT_TYPE,
    )


    print()
    print("--- AMF EVIDENCE REPORT ---")

    print(
        f"Test: "
        f"{report['test']['id']}"
    )

    print(
        f"Source SCAS test: "
        f"{report['test']['source_test_name']}"
    )


    static_results = [
        result
        for result in report["verification"]["results"]
        if result["engine"] == "simple_verifier"
    ]

    static_verdict = (
        "PASS" if all(
            result["verdict"] == "PASS"
            for result in static_results
        )
        else "FAIL"
    )


    temporal_results = [
        result
        for result in report["verification"]["results"] 
        if result["engine"] != "simple_verifier"
    ]

    temporal_verdict = (
        temporal_results[0]["verdict"]
        if temporal_results
        else "N/A"
    )


    print(
        f"Static verdict: {static_verdict}"
    )

    print(
        f"Temporal verdict: {temporal_verdict}"
    )

    print(
        f"Overall verdict: {report['verdict']}"
    )

    print(
        f"Report saved to: {output_file}"
    )

    print("---------------------------")



if __name__ == "__main__":
    main()