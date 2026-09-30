from pathlib import Path

import utils.reporter_utils as reporter_utils
from utils.report_schema import normalize_report


BASE_DIR = Path(__file__).resolve().parent.parent


EVENT_TYPE = "pfcp_session_establishment_response"


def build_observed_responses(events):
    responses = []

    for event in events:
        responses.append({
            "frame": event["frame"],
            "timestamp_relative": event["timestamp_relative"],
            "timestamp_epoch": event["timestamp_epoch"],
            "ip_src": event["ip_src"],
            "ip_dst": event["ip_dst"],
            "f_teids": event["f_teids"]            
        })

    return responses


def build_report(test_id, case_id, context):
    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]
    events = context["event"]


    # Il test UPF contiene una sola regola DSl
    rule_result = verification["rules"][0]
    parsed_rule = parsed_rules[0]

    criterion_id = "criterion_1"

    observed_responses = build_observed_responses(events)

    evidence_frames = [
        event["frame"]
        for event in events
    ]

    session_establishment_responses = len(events)

    f_teids_observed = sum(
        len(event["f_teids"])
        for event in events
    )

    duplicates = rule_result.get("duplicates", [])

    rule_expression = f"REQUIRE UNIQUE {parsed_rule['field']}"


    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "source_test_name": "TC_TEID_ID_UNIQUENESS_UPF",

            "nf": "UPF",

            "description": "Verification of F-TEID uniqueness across PFCP Session Establishment Responses"
        },

        "source": evidence["source"],

        "criteria": [
            {
                "id": criterion_id,

                "type": "uniqueness",

                "description": "F-TEIDs observed in PFCP Session Establishment Responses must not be reused across different responses for the same UPF IP address",

                "specification": {
                    "language": "DSL",
                    "expression": rule_expression
                }
            }
        ],

        "verification": {
            "results": [
                {
                    "criterion_id": criterion_id,

                    "engine": "simple_verifier",

                    "field": rule_result["field"],

                    "operator": rule_result["operator"],

                    "expected": rule_result["expected"],

                    "observed": rule_result["observed"],

                    "duplicates": duplicates,

                    "evidence_frames": evidence_frames,

                    "verdict": rule_result["verdict"]
                }
            ],

            "overall_verdict": verification["overall_verdict"]
        },

        "evidence": {
            "type": EVENT_TYPE,

            "pfcp_message_type": 51,

            "responses": observed_responses
        },

        "explanation": {
            "session_establishment_responses": session_establishment_responses,

            "f_teids_observed": f_teids_observed,

            "duplicates_found": len(duplicates)
        },

        "verdict": verification["overall_verdict"]
    }


    if duplicates:
        duplicate_name = "F-TIED" if len(duplicates) == 1 else "F-TIEDs"
        summary = (
            f"Detected {len(duplicates)} {duplicate_name} reused across "
            f"{session_establishment_responses} PFCP Session Establishment Responses."
        )
    else:
        summary = (
            f"No F-TEID was reused across {session_establishment_responses} "
            f"PFCP Session Establishment Responses ({f_teids_observed} observed)."
        )

    return normalize_report(report, summary)    



def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR,
        "Generate UPF F-TIED uniqueness report",
        build_report,
        EVENT_TYPE,
        require_single_event=False
    )

    observations = report["explanation"]["observations"]


    reporter_utils.save_json(output_file, report)


    print()
    print("--- UPF EVIDENCE REPORT ---")

    print(
        f"Test: {report['test']['id']}"
    )

    print(
        f"Source SCAS test: {report['test']['source_test_name']}"
    )

    print(
        f"NF: {report['test']['nf']}"
    )

    print(
        f"PFCP Session Establishment Responses: {observations['session_establishment_responses']}"
    )

    print(
        f"F-TEIDs observed: {observations['f_teids_observed']}"
    )

    duplicates = (
        report["verification"]["results"][0]["details"]["duplicates"]
    )

    if duplicates:
        print("Duplicate F-TEIDs:")

        for duplicate in duplicates:
            value = duplicate["value"]

            print(
                f"- {value['teid']} "
                f"@ {value['ipv4']} "
                f"in frames "
                f"{duplicate['frames']}"
            )

    else:
        print(
            "No F-TEID reused across different responses."
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