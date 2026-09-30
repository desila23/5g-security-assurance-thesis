from pathlib import Path

import utils.reporter_utils as reporter_utils

from utils.report_schema import normalize_report


BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_TYPE = "nrf_nf_discovery"


def build_report(test_id, case_id, context):
    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]
    event = context["event"]

    verification_rule = verification["rules"][0]
    parsed_rule = parsed_rules[0]

    request_frame = event["request"]["frame"]
    response_frame = event["response"]["frame"]
    body_frame = event["body"]["frame"]

    criterion_id = "criterion_1"

    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "source_test_name": (
                "TC DISC AUTH SLICE"
            ),

            "nf": "NRF",

            "description": (
                "Verification of NF Discovery authorization "
                "under slice constraints"
            ),
        },

        "source": evidence["source"],

        "criteria": [
            {
                "id": criterion_id,

                "type": "comparison",

                "description": (
                    "The NF Discovery request must receive "
                    "HTTP status 403"
                ),

                "specification": {
                    "language": "DSL",

                    "expression": (
                        reporter_utils.rule_to_expression(
                            parsed_rule
                        )
                    ),
                },
            }
        ],

        "verification": {
            "results": [
                {
                    "criterion_id": criterion_id,

                    "engine": "simple_verifier",

                    "field": (
                        verification_rule["field"]
                    ),

                    "operator": (
                        verification_rule["operator"]
                    ),

                    "expected": (
                        verification_rule["expected"]
                    ),

                    "observed": (
                        verification_rule["observed"]
                    ),

                    "evidence_frames": [
                        request_frame,
                        response_frame,
                        body_frame,
                    ],

                    "verdict": (
                        verification_rule["verdict"]
                    ),
                }
            ],

            "overall_verdict": (
                verification["overall_verdict"]
            ),
        },

        "evidence": {
            "type": EVENT_TYPE,

            "request": (
                event["request"]
            ),

            "response": (
                event["response"]
            ),

            "body": (
                event["body"]
            ),
        },

        "explanation": {
            "requester_nf": (
                event["request"].get(
                    "requester_nf_type"
                )
            ),

            "requester_snssais": (
                event["request"].get(
                    "requester_snssais"
                )
            ),

            "target_nf": (
                event["request"].get(
                    "target_nf_type"
                )
            ),

            "expected_http_status": (
                verification_rule["expected"]
            ),

            "observed_http_status": (
                verification_rule["observed"]
            ),
        },

        "verdict": (
            verification["overall_verdict"]
        ),
    }

    expected = verification_rule["expected"]
    observed = verification_rule["observed"]
    summary = (
        f"Expected HTTP {expected} from NF Discovery; observed HTTP {observed}"
    )

    return normalize_report(report, summary)



def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR, 
        "Generate NRF NF Discovery authorization report",
        build_report,
        EVENT_TYPE,        
    )


    print()
    print("--- EVIDENCE REPORT ---")

    print(
        f"Test: {report['test']['id']}"
    )

    print(
        f"Source SCAS test: "
        f"{report['test']['source_test_name']}"
    )

    print(
        f"NF: {report['test']['nf']}"
    )

    print(
        f"Overall verdict: "
        f"{report['verification']['overall_verdict']}"
    )

    print(
        f"Report saved to: {output_file}"
    )

    print("-----------------------")



if __name__ == "__main__":
    main()