from pathlib import Path

import utils.reporter_utils as reporter_utils
from utils.report_schema import normalize_report


BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_TYPE = "resstar_verification_failure"


def get_frames_for_field(event, field_path):
    parts = field_path.split(".")

    # Remove event type
    nested_parts = parts[1:]

    if not nested_parts:
        return []

    section = nested_parts[0]


    # HRES* deriva da RAND, RES* e HXRES*
    if section == "res_star_verification":
        frames = []

        for source_section in [
            "authentication_vector",
            "authentication_request",
            "authentication_response"
        ]:
            source_data = event.get(source_section)

            if not isinstance(source_data, dict):
                continue

            frame = source_data.get("frame")

            if frame is not None:
                frames.append(frame)

        return list(dict.fromkeys(frames))

    section_data = event.get(section)

    if not isinstance(section_data, dict):
        return []

    frame = section_data.get("frame")

    if frame is None:
        return []

    return [frame]



# -- VERIFICATION REPORTING --
def build_rule_report(
    event,
    parsed_rule,
    verification_rule,
    criterion_id,
):
    operator = verification_rule["operator"]

    criterion_type = (
        "conditional"
        if operator == "IF"
        else "comparison"
    )

    if operator == "IF":
        description = f"Conditional verification for {verification_rule['field']}"

        specification = {
            "language": "DSL",
            "condition": {
                "field": parsed_rule["field"],
                "operator": parsed_rule[
                    "condition_operator"
                ],
                "expected": reporter_utils.operand_to_text(
                    parsed_rule["expected"]
                ),
            },
            "rules": [
                reporter_utils.rule_to_expression(rule)
                for rule in parsed_rule["rules"]
            ],
        }

    else:
        description = f"Verification of {verification_rule['field']} {operator}"

        specification = {
            "language": "DSL",
            "expression": reporter_utils.rule_to_expression(
                parsed_rule
            ),
        }


    criterion = {
        "id": criterion_id,
        "type": criterion_type,
        "description": description,
        "specification": specification,
    }


    result = {
        "criterion_id": criterion_id,

        "engine": "simple_verifier",

        "field": verification_rule["field"],

        "operator": operator,

        "expected": verification_rule.get("expected"),

        "observed": verification_rule.get("observed"),

        "evidence_frames": get_frames_for_field(
            event,
            verification_rule["field"],
        ),

        "verdict": verification_rule["verdict"]        
    }


    if operator == "IF":
        result["condition_operator"] = verification_rule["condition_operator"]

        nested_results = []

        parsed_nested_rules = parsed_rule["rules"]
        verified_nested_rules = verification_rule["rules"]


        for index , (parsed_nested, verified_nested) in enumerate (
            zip(parsed_nested_rules, verified_nested_rules), start=1):
                nested_id = f"{criterion_id}.{index}"

                nested_criterion, nested_result = (
                    build_rule_report(event, parsed_nested, verified_nested, nested_id)
                )

                nested_results.append({
                    "criterion": nested_criterion,
                    "result": nested_result
                })

        result["rules"] = nested_results

    return criterion, result



# -- EXPLANATION --
def build_explanation(event):
    identity_request = event.get("identity_request")
    identity_response = event.get("identity_response")
    ausf_request = event.get("ausf_confirmation_request")
    ausf_response = event.get("ausf_confirmation_response")

    explanation = {
        "case": event["case"],
        "identity_path": event["identity_path"],
        "failure_source": event["failure_source"],

        "authentication_reject_present": event["authentication_reject"]["present"],

        "hres_star": event["res_star_verification"]["hres_star"],

        "hxres_star": event["res_star_verification"]["hxres_star"],

        "hres_hxres_match": event["res_star_verification"]["match"],        


        "identity_request_present": identity_request is not None,

        "requested_identity": (
            identity_request.get("requested_identity")
            if identity_request
            else None
        ),


        "identity_response_present": identity_response is not None,

        "identity_response_type": (
            identity_response.get("identity_type")
            if identity_response
            else None
        ),


        "ausf_confirmation_request_present": ausf_request is not None,

        "ausf_confirmation_res_star": (
            ausf_request.get("res_star")
            if ausf_request
            else None
        ),


        "ausf_confirmation_response_present": ausf_response is not None,

        "ausf_auth_result": (
            ausf_response.get("auth_result")
            if ausf_response
            else None
        ),
    }

    return explanation



# -- REPORT --
def build_report(test_id, case_id, context):
    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]
    event = context["event"]


    criteria = []
    verification_results = []

    for index, (parsed_rule, verification_rule) in enumerate (
        zip(parsed_rules, verification["rules"]), start=1
    ):
        criterion_id = f"criterion_{index}"

        criterion, result = build_rule_report(event, parsed_rule, verification_rule, criterion_id)

        criteria.append(criterion)

        verification_results.append(result)

    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "case": case_id,

            "source_test_name": f"TC_RESSTAR_VERIFICATION_FAILURE - Test {case_id}",

            "nf": "AMF",

            "description": "Verification of RES* handling by the SEAF/AMF, including local HRES*/HXRES* verification and AUSF confirmation handling",
        },

        "source": evidence["source"],

        "criteria": criteria,

        "verification": {
            "results": verification_results,

            "overall_verdict": verification["overall_verdict"],
        },

        "evidence": event,

        "explanation": build_explanation(event),

        "verdict": verification["overall_verdict"]
    }


    failure_source = event["failure_source"]
    identity_path = {
        "direct_suci": "direct SUCI",
        "guti_then_suci": "GUTI then SUCI",
    }.get(event["identity_path"], event["identity_path"])

    if failure_source == "local":
        comparison = (
            "match" if event["res_star_verification"]["match"] else "differ"
        )
        summary = (
            f"Case {case_id} ({identity_path}): local HRES* and HXRES* "
            f"{comparison}; overall verdict {verification['overall_verdict']}."
        )
    elif failure_source == "ausf":
        ausf_response = event.get("ausf_confirmation_response") or {}
        auth_result = ausf_response.get("auth_result", "missing")
        summary = (
            f"Case {case_id} ({identity_path}): AUSF authentication result "
            f"{auth_result}; overall verdict {verification['overall_verdict']}."
        )
    else:
        raise ValueError(f"Unsupported failure source: {failure_source}")

    return normalize_report(report, summary)


# -- MAIN -- 
def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR,
        "Generate RES* verification failure report",
        build_report,
        EVENT_TYPE
    )

    observations = report["explanation"]["observations"]


    print()
    print("--- RES* EVIDENCE REPORT ---")

    print(
        f"Test: {report['test']['id']}"
    )

    print(
        f"Case: {report['test']['case']}"
    )

    print(
        "Source SCAS test: "
        f"{report['test']['source_test_name']}"
    )

    print(
        "Identity path: "
        f"{observations['identity_path']}"
    )

    print(
        "Failure source: "
        f"{observations['failure_source']}"
    )

    print(
        "HRES*/HXRES* match: "
        f"{observations['hres_hxres_match']}"
    )

    if (
        observations["failure_source"] == "ausf"
    ):
        print(
            "AUSF authentication result: "
            f"{observations.get('ausf_auth_result')}"
        )

    print(
        "Overall verdict: "
        f"{report['verdict']}"
    )

    print(
        f"Report saved to: {output_file}"
    )

    print("---------------------------")


if __name__ == "__main__":
    main()